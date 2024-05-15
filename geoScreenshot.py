import pandas as pd
from selenium import webdriver
import time

df = pd.read_csv('geoInfo.csv', encoding='cp949', dtype=str, low_memory=False)
df['건축물면적(m^2)'] = df['건축물면적(m^2)'].astype(float)

df['건물명'] = df['건물명'].fillna('')
df['건축물용도명'] = df['건축물용도명'].fillna('')
df['건물동명'] = df['건물동명'].fillna('')

filtered_df = df[(df['건축물면적(m^2)'] >= 925) & 
                 (df['법정동명'].str.contains('마포구|구로구')) & 
                 (df['건축물구조명'] == '철근콘크리트구조') & 
                 (~df['건축물용도명'].str.contains('주택')) & 
                 (~df['건물명'].str.contains('중학교|고등학교|초등학교'))]

selected_columns = filtered_df[['GIS건물통합식별번호', '법정동명', '건축물면적(m^2)', 'y', 'x', '건물명', '건물동명']]
selected_columns = selected_columns.reset_index(drop=True)
options = webdriver.SafariOptions()

try:
    driver = webdriver.Safari(options=options)
    driver.quit()
except Exception as e:
    print(f"Error during initial driver quit: {e}")

driver = webdriver.Safari(options=options)


def generate_html(latitude, longitude, zoom):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>브이월드 지도</title>
    <script type="text/javascript" src="https://map.vworld.kr/js/vworldMapInit.js.do?version=2.0&apiKey=92F3EA05-2445-3421-9F3F-9537BC9BC978"></script>
    <style>
        #vmap {{
            width: 100%;
            height: 75vh; /* 화면 높이의 75%를 차지 */
            left: 0px;
            top: 0px;
        }}
        #buttons {{
            margin-top: 10px;
        }}
    </style>
    </head>
    <body>
     <div id="vmap"></div>
     <script type="text/javascript">
      vw.ol3.MapOptions = {{
          basemapType: vw.ol3.BasemapType.PHOTO,  // 기본 지도 타입을 항공사진으로 설정
          controlDensity: vw.ol3.DensityType.EMPTY,
          interactionDensity: vw.ol3.DensityType.BASIC,
          controlsAutoArrange: true,
          homePosition: vw.ol3.CameraPosition,
          initPosition: vw.ol3.CameraPosition
      }};
         
      var vmap = new vw.ol3.Map("vmap", vw.ol3.MapOptions);
      
      
      function moveToLocation() {{
          var position = ol.proj.fromLonLat([{longitude}, {latitude}]);
          vmap.getView().setCenter(position);
          vmap.getView().setZoom({zoom});

          
          var markerLayer = new vw.ol3.layer.Marker(vmap);
          vmap.addLayer(markerLayer);

          
          var marker = new vw.ol3.marker({{
              position: position,
              map: vmap
          }});
          
          markerLayer.addMarker(marker);
      }}

      document.addEventListener('DOMContentLoaded', function() {{
          moveToLocation();
      }});
     </script>
    </body>
    </html>
    """
    with open("map.html", "w", encoding="utf-8") as file:
        file.write(html_content)

for index, row in selected_columns.iterrows():
    latitude = float(row['y'])
    longitude = float(row['x'])
    zoom = 25 

    generate_html(latitude, longitude, zoom)

    driver.get("file:///Users/kimjongjip/ninewat/map.html") 
    time.sleep(5)  

   
    screenshot_path = f"screenshot_{index}.png"
    driver.save_screenshot(screenshot_path)
    print(f"Saved screenshot: {screenshot_path}")

driver.quit()
