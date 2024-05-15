import pandas as pd
from selenium import webdriver
import time

# CSV 파일을 'cp949' 인코딩으로 불러옵니다
df = pd.read_csv('geoInfo.csv', encoding='cp949', dtype=str, low_memory=False)

# 건축물면적을 float 타입으로 변환하여 필터링
df['건축물면적(m^2)'] = df['건축물면적(m^2)'].astype(float)

# 결측값 채우기
df['건물명'] = df['건물명'].fillna('')
df['건축물용도명'] = df['건축물용도명'].fillna('')
df['건물동명'] = df['건물동명'].fillna('')

# 조건에 맞게 데이터 필터링
filtered_df = df[(df['건축물면적(m^2)'] >= 925) & 
                 (df['법정동명'].str.contains('마포구|구로구')) & 
                 (df['건축물구조명'] == '철근콘크리트구조') & 
                 (~df['건축물용도명'].str.contains('주택')) & 
                 (~df['건물명'].str.contains('중학교|고등학교|초등학교'))]

# 필요한 열만 선택하여 출력
selected_columns = filtered_df[['GIS건물통합식별번호', '법정동명', '건축물면적(m^2)', 'y', 'x', '건물명', '건물동명']]

# 인덱스 재설정
selected_columns = selected_columns.reset_index(drop=True)

# Selenium 설정
options = webdriver.SafariOptions()

# SafariDriver 세션 초기화
try:
    driver = webdriver.Safari(options=options)
    driver.quit()
except Exception as e:
    print(f"Error during initial driver quit: {e}")

# 새로운 SafariDriver 세션 시작
driver = webdriver.Safari(options=options)

# HTML 파일 생성 함수
def generate_html(latitude, longitude, zoom):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>브이월드 지도</title>
    <script type="text/javascript" src="https://map.vworld.kr/js/vworldMapInit.js.do?version=2.0&apiKey=92F3EA05-2445-3421-9F3F-9537BC9BC978"></script>
    <style>
        #vmap1 {{
            width: 49%;
            height: 75vh; /* 화면 높이의 75%를 차지 */
            display: inline-block;
        }}
        #vmap2 {{
            width: 49%;
            height: 75vh; /* 화면 높이의 75%를 차지 */
            display: inline-block;
        }}
    </style>
    </head>
    <body>
     <div id="vmap1"></div>
     <div id="vmap2"></div>
     <script type="text/javascript">
      var mapOptions1 = {{
          basemapType: vw.ol3.BasemapType.GRAPHIC,  // 기본 지도 타입을 배경지도로 설정
          controlDensity: vw.ol3.DensityType.EMPTY,
          interactionDensity: vw.ol3.DensityType.BASIC,
          controlsAutoArrange: true,
          homePosition: vw.ol3.CameraPosition,
          initPosition: vw.ol3.CameraPosition
      }};
      
      var mapOptions2 = {{
          basemapType: vw.ol3.BasemapType.PHOTO,  // 기본 지도 타입을 항공사진으로 설정
          controlDensity: vw.ol3.DensityType.EMPTY,
          interactionDensity: vw.ol3.DensityType.BASIC,
          controlsAutoArrange: true,
          homePosition: vw.ol3.CameraPosition,
          initPosition: vw.ol3.CameraPosition
      }};
      
      var vmap1 = new vw.ol3.Map("vmap1", mapOptions1);
      var vmap2 = new vw.ol3.Map("vmap2", mapOptions2);

      // 특정 좌표로 이동하고 마커를 추가하는 함수
      function moveToLocation(map, longitude, latitude, zoom) {{
          var position = ol.proj.fromLonLat([longitude, latitude]);
          map.getView().setCenter(position);
          map.getView().setZoom(zoom);

          // 마커 옵션 설정
          var markerOption = {{
              x: longitude,
              y: latitude,
              epsg: "EPSG:4326",
              title: '기본 마커',
              iconUrl: 'http://map.vworld.kr/images/ol3/marker_blue.png',
              text: {{
                  offsetX: 0.5,
                  offsetY: 20,
                  font: '12px Calibri,sans-serif',
                  fill: {{color: '#000'}},
                  stroke: {{color: '#fff', width: 2}},
              }},
              attr: {{"id": "defaultMarker", "name": "기본 마커"}}
          }};

          // 마커 레이어 생성
          var markerLayer = new vw.ol3.layer.Marker(map);
          map.addLayer(markerLayer);

          // 마커 추가
          markerLayer.addMarker(markerOption);
      }}

      // 페이지 로드 시 기본 위치로 이동하고 마커 추가
      document.addEventListener('DOMContentLoaded', function() {{
          moveToLocation(vmap1, {longitude}, {latitude}, {zoom});
          moveToLocation(vmap2, {longitude}, {latitude}, {zoom});
      }});
     </script>
    </body>
    </html>
    """
    with open("map.html", "w", encoding="utf-8") as file:
        file.write(html_content)

# 데이터프레임의 각 행에 대해 HTML 파일을 생성하고 브라우저에서 열어 스크린샷 저장
for index, row in selected_columns.iterrows():
    latitude = float(row['y'])
    longitude = float(row['x'])
    zoom = 25  # 줌 레벨을 25로 설정하여 더 확대된 상태로 캡처

    generate_html(latitude, longitude, zoom)

    driver.get("file:///Users/kimjongjip/ninewat/map.html")  # HTML 파일 경로 설정
    time.sleep(5)  # 지도가 로드될 시간을 기다림

    # 스크린샷 저장
    screenshot_path = f"screenshot_{index}.png"
    driver.save_screenshot(screenshot_path)
    print(f"Saved screenshot: {screenshot_path}")

driver.quit()
