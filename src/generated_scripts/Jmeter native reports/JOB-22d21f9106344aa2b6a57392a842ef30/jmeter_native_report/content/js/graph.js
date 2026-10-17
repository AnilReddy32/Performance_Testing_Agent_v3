/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
$(document).ready(function() {

    $(".click-title").mouseenter( function(    e){
        e.preventDefault();
        this.style.cursor="pointer";
    });
    $(".click-title").mousedown( function(event){
        event.preventDefault();
    });

    // Ugly code while this script is shared among several pages
    try{
        refreshHitsPerSecond(true);
    } catch(e){}
    try{
        refreshResponseTimeOverTime(true);
    } catch(e){}
    try{
        refreshResponseTimePercentiles();
    } catch(e){}
});


var responseTimePercentilesInfos = {
        data: {"result": {"minY": 153.0, "minX": 0.0, "maxY": 3502.0, "series": [{"data": [[0.0, 153.0], [0.1, 153.0], [0.2, 153.0], [0.3, 154.0], [0.4, 154.0], [0.5, 158.0], [0.6, 158.0], [0.7, 158.0], [0.8, 158.0], [0.9, 160.0], [1.0, 162.0], [1.1, 162.0], [1.2, 163.0], [1.3, 165.0], [1.4, 165.0], [1.5, 165.0], [1.6, 167.0], [1.7, 167.0], [1.8, 167.0], [1.9, 168.0], [2.0, 168.0], [2.1, 168.0], [2.2, 168.0], [2.3, 168.0], [2.4, 169.0], [2.5, 169.0], [2.6, 170.0], [2.7, 171.0], [2.8, 171.0], [2.9, 171.0], [3.0, 172.0], [3.1, 172.0], [3.2, 172.0], [3.3, 173.0], [3.4, 173.0], [3.5, 174.0], [3.6, 174.0], [3.7, 175.0], [3.8, 176.0], [3.9, 179.0], [4.0, 179.0], [4.1, 180.0], [4.2, 182.0], [4.3, 182.0], [4.4, 186.0], [4.5, 187.0], [4.6, 188.0], [4.7, 188.0], [4.8, 193.0], [4.9, 206.0], [5.0, 206.0], [5.1, 207.0], [5.2, 209.0], [5.3, 215.0], [5.4, 215.0], [5.5, 224.0], [5.6, 224.0], [5.7, 224.0], [5.8, 225.0], [5.9, 230.0], [6.0, 231.0], [6.1, 231.0], [6.2, 232.0], [6.3, 234.0], [6.4, 234.0], [6.5, 239.0], [6.6, 247.0], [6.7, 250.0], [6.8, 250.0], [6.9, 252.0], [7.0, 259.0], [7.1, 259.0], [7.2, 259.0], [7.3, 262.0], [7.4, 264.0], [7.5, 264.0], [7.6, 264.0], [7.7, 265.0], [7.8, 265.0], [7.9, 265.0], [8.0, 265.0], [8.1, 269.0], [8.2, 269.0], [8.3, 269.0], [8.4, 270.0], [8.5, 271.0], [8.6, 271.0], [8.7, 272.0], [8.8, 272.0], [8.9, 272.0], [9.0, 272.0], [9.1, 273.0], [9.2, 273.0], [9.3, 273.0], [9.4, 273.0], [9.5, 274.0], [9.6, 274.0], [9.7, 277.0], [9.8, 278.0], [9.9, 278.0], [10.0, 278.0], [10.1, 278.0], [10.2, 278.0], [10.3, 278.0], [10.4, 279.0], [10.5, 279.0], [10.6, 279.0], [10.7, 279.0], [10.8, 279.0], [10.9, 279.0], [11.0, 279.0], [11.1, 280.0], [11.2, 280.0], [11.3, 280.0], [11.4, 280.0], [11.5, 280.0], [11.6, 280.0], [11.7, 281.0], [11.8, 281.0], [11.9, 281.0], [12.0, 281.0], [12.1, 281.0], [12.2, 281.0], [12.3, 282.0], [12.4, 282.0], [12.5, 282.0], [12.6, 282.0], [12.7, 282.0], [12.8, 282.0], [12.9, 282.0], [13.0, 282.0], [13.1, 282.0], [13.2, 282.0], [13.3, 282.0], [13.4, 283.0], [13.5, 283.0], [13.6, 283.0], [13.7, 283.0], [13.8, 283.0], [13.9, 283.0], [14.0, 284.0], [14.1, 284.0], [14.2, 284.0], [14.3, 284.0], [14.4, 284.0], [14.5, 284.0], [14.6, 284.0], [14.7, 284.0], [14.8, 284.0], [14.9, 284.0], [15.0, 284.0], [15.1, 284.0], [15.2, 284.0], [15.3, 284.0], [15.4, 284.0], [15.5, 285.0], [15.6, 285.0], [15.7, 285.0], [15.8, 285.0], [15.9, 285.0], [16.0, 285.0], [16.1, 286.0], [16.2, 286.0], [16.3, 286.0], [16.4, 286.0], [16.5, 286.0], [16.6, 286.0], [16.7, 286.0], [16.8, 287.0], [16.9, 287.0], [17.0, 287.0], [17.1, 287.0], [17.2, 287.0], [17.3, 287.0], [17.4, 287.0], [17.5, 287.0], [17.6, 287.0], [17.7, 287.0], [17.8, 287.0], [17.9, 287.0], [18.0, 287.0], [18.1, 287.0], [18.2, 287.0], [18.3, 287.0], [18.4, 288.0], [18.5, 288.0], [18.6, 288.0], [18.7, 288.0], [18.8, 288.0], [18.9, 288.0], [19.0, 288.0], [19.1, 288.0], [19.2, 288.0], [19.3, 288.0], [19.4, 288.0], [19.5, 288.0], [19.6, 288.0], [19.7, 288.0], [19.8, 288.0], [19.9, 288.0], [20.0, 288.0], [20.1, 288.0], [20.2, 288.0], [20.3, 288.0], [20.4, 289.0], [20.5, 289.0], [20.6, 289.0], [20.7, 289.0], [20.8, 289.0], [20.9, 289.0], [21.0, 289.0], [21.1, 289.0], [21.2, 289.0], [21.3, 289.0], [21.4, 289.0], [21.5, 289.0], [21.6, 289.0], [21.7, 289.0], [21.8, 289.0], [21.9, 289.0], [22.0, 289.0], [22.1, 290.0], [22.2, 290.0], [22.3, 290.0], [22.4, 290.0], [22.5, 290.0], [22.6, 290.0], [22.7, 290.0], [22.8, 290.0], [22.9, 290.0], [23.0, 290.0], [23.1, 290.0], [23.2, 290.0], [23.3, 290.0], [23.4, 290.0], [23.5, 290.0], [23.6, 290.0], [23.7, 290.0], [23.8, 290.0], [23.9, 290.0], [24.0, 290.0], [24.1, 291.0], [24.2, 291.0], [24.3, 291.0], [24.4, 291.0], [24.5, 291.0], [24.6, 291.0], [24.7, 291.0], [24.8, 291.0], [24.9, 291.0], [25.0, 291.0], [25.1, 291.0], [25.2, 291.0], [25.3, 292.0], [25.4, 292.0], [25.5, 292.0], [25.6, 292.0], [25.7, 292.0], [25.8, 292.0], [25.9, 292.0], [26.0, 292.0], [26.1, 292.0], [26.2, 292.0], [26.3, 292.0], [26.4, 292.0], [26.5, 292.0], [26.6, 292.0], [26.7, 292.0], [26.8, 292.0], [26.9, 292.0], [27.0, 292.0], [27.1, 292.0], [27.2, 292.0], [27.3, 292.0], [27.4, 292.0], [27.5, 292.0], [27.6, 293.0], [27.7, 293.0], [27.8, 293.0], [27.9, 293.0], [28.0, 293.0], [28.1, 293.0], [28.2, 293.0], [28.3, 293.0], [28.4, 293.0], [28.5, 293.0], [28.6, 293.0], [28.7, 293.0], [28.8, 293.0], [28.9, 294.0], [29.0, 294.0], [29.1, 294.0], [29.2, 294.0], [29.3, 294.0], [29.4, 294.0], [29.5, 294.0], [29.6, 294.0], [29.7, 294.0], [29.8, 294.0], [29.9, 294.0], [30.0, 294.0], [30.1, 294.0], [30.2, 294.0], [30.3, 294.0], [30.4, 294.0], [30.5, 294.0], [30.6, 294.0], [30.7, 294.0], [30.8, 294.0], [30.9, 294.0], [31.0, 294.0], [31.1, 294.0], [31.2, 294.0], [31.3, 294.0], [31.4, 294.0], [31.5, 295.0], [31.6, 295.0], [31.7, 295.0], [31.8, 295.0], [31.9, 295.0], [32.0, 295.0], [32.1, 295.0], [32.2, 295.0], [32.3, 295.0], [32.4, 295.0], [32.5, 295.0], [32.6, 295.0], [32.7, 295.0], [32.8, 295.0], [32.9, 295.0], [33.0, 295.0], [33.1, 295.0], [33.2, 295.0], [33.3, 295.0], [33.4, 295.0], [33.5, 295.0], [33.6, 295.0], [33.7, 295.0], [33.8, 295.0], [33.9, 295.0], [34.0, 295.0], [34.1, 295.0], [34.2, 295.0], [34.3, 295.0], [34.4, 295.0], [34.5, 296.0], [34.6, 296.0], [34.7, 296.0], [34.8, 296.0], [34.9, 296.0], [35.0, 296.0], [35.1, 296.0], [35.2, 296.0], [35.3, 296.0], [35.4, 296.0], [35.5, 296.0], [35.6, 296.0], [35.7, 296.0], [35.8, 296.0], [35.9, 296.0], [36.0, 296.0], [36.1, 296.0], [36.2, 296.0], [36.3, 296.0], [36.4, 296.0], [36.5, 296.0], [36.6, 296.0], [36.7, 297.0], [36.8, 297.0], [36.9, 297.0], [37.0, 297.0], [37.1, 297.0], [37.2, 297.0], [37.3, 297.0], [37.4, 297.0], [37.5, 297.0], [37.6, 297.0], [37.7, 297.0], [37.8, 297.0], [37.9, 297.0], [38.0, 297.0], [38.1, 297.0], [38.2, 297.0], [38.3, 297.0], [38.4, 297.0], [38.5, 297.0], [38.6, 297.0], [38.7, 297.0], [38.8, 298.0], [38.9, 298.0], [39.0, 298.0], [39.1, 298.0], [39.2, 298.0], [39.3, 298.0], [39.4, 298.0], [39.5, 298.0], [39.6, 298.0], [39.7, 298.0], [39.8, 298.0], [39.9, 298.0], [40.0, 298.0], [40.1, 298.0], [40.2, 298.0], [40.3, 298.0], [40.4, 298.0], [40.5, 298.0], [40.6, 298.0], [40.7, 299.0], [40.8, 299.0], [40.9, 299.0], [41.0, 299.0], [41.1, 299.0], [41.2, 299.0], [41.3, 299.0], [41.4, 299.0], [41.5, 299.0], [41.6, 299.0], [41.7, 299.0], [41.8, 299.0], [41.9, 299.0], [42.0, 299.0], [42.1, 299.0], [42.2, 299.0], [42.3, 299.0], [42.4, 299.0], [42.5, 300.0], [42.6, 300.0], [42.7, 300.0], [42.8, 300.0], [42.9, 300.0], [43.0, 300.0], [43.1, 300.0], [43.2, 300.0], [43.3, 300.0], [43.4, 300.0], [43.5, 300.0], [43.6, 300.0], [43.7, 300.0], [43.8, 300.0], [43.9, 300.0], [44.0, 300.0], [44.1, 301.0], [44.2, 301.0], [44.3, 301.0], [44.4, 301.0], [44.5, 301.0], [44.6, 301.0], [44.7, 301.0], [44.8, 301.0], [44.9, 301.0], [45.0, 301.0], [45.1, 301.0], [45.2, 301.0], [45.3, 301.0], [45.4, 301.0], [45.5, 301.0], [45.6, 301.0], [45.7, 301.0], [45.8, 301.0], [45.9, 302.0], [46.0, 302.0], [46.1, 302.0], [46.2, 302.0], [46.3, 302.0], [46.4, 302.0], [46.5, 302.0], [46.6, 302.0], [46.7, 302.0], [46.8, 302.0], [46.9, 302.0], [47.0, 302.0], [47.1, 302.0], [47.2, 302.0], [47.3, 302.0], [47.4, 302.0], [47.5, 302.0], [47.6, 302.0], [47.7, 302.0], [47.8, 302.0], [47.9, 302.0], [48.0, 302.0], [48.1, 302.0], [48.2, 303.0], [48.3, 303.0], [48.4, 303.0], [48.5, 303.0], [48.6, 303.0], [48.7, 303.0], [48.8, 303.0], [48.9, 303.0], [49.0, 303.0], [49.1, 303.0], [49.2, 303.0], [49.3, 303.0], [49.4, 303.0], [49.5, 303.0], [49.6, 303.0], [49.7, 303.0], [49.8, 303.0], [49.9, 303.0], [50.0, 303.0], [50.1, 303.0], [50.2, 303.0], [50.3, 303.0], [50.4, 303.0], [50.5, 304.0], [50.6, 304.0], [50.7, 304.0], [50.8, 304.0], [50.9, 304.0], [51.0, 304.0], [51.1, 304.0], [51.2, 304.0], [51.3, 304.0], [51.4, 304.0], [51.5, 304.0], [51.6, 304.0], [51.7, 304.0], [51.8, 304.0], [51.9, 304.0], [52.0, 304.0], [52.1, 304.0], [52.2, 304.0], [52.3, 304.0], [52.4, 304.0], [52.5, 304.0], [52.6, 305.0], [52.7, 305.0], [52.8, 305.0], [52.9, 305.0], [53.0, 305.0], [53.1, 305.0], [53.2, 305.0], [53.3, 305.0], [53.4, 305.0], [53.5, 306.0], [53.6, 306.0], [53.7, 306.0], [53.8, 306.0], [53.9, 306.0], [54.0, 306.0], [54.1, 307.0], [54.2, 307.0], [54.3, 307.0], [54.4, 307.0], [54.5, 307.0], [54.6, 307.0], [54.7, 307.0], [54.8, 307.0], [54.9, 307.0], [55.0, 307.0], [55.1, 307.0], [55.2, 307.0], [55.3, 307.0], [55.4, 307.0], [55.5, 307.0], [55.6, 307.0], [55.7, 307.0], [55.8, 307.0], [55.9, 307.0], [56.0, 307.0], [56.1, 307.0], [56.2, 307.0], [56.3, 307.0], [56.4, 307.0], [56.5, 308.0], [56.6, 308.0], [56.7, 308.0], [56.8, 308.0], [56.9, 308.0], [57.0, 308.0], [57.1, 308.0], [57.2, 308.0], [57.3, 308.0], [57.4, 308.0], [57.5, 308.0], [57.6, 308.0], [57.7, 309.0], [57.8, 309.0], [57.9, 309.0], [58.0, 309.0], [58.1, 309.0], [58.2, 309.0], [58.3, 309.0], [58.4, 309.0], [58.5, 309.0], [58.6, 309.0], [58.7, 309.0], [58.8, 309.0], [58.9, 309.0], [59.0, 309.0], [59.1, 309.0], [59.2, 309.0], [59.3, 309.0], [59.4, 309.0], [59.5, 309.0], [59.6, 309.0], [59.7, 309.0], [59.8, 310.0], [59.9, 310.0], [60.0, 310.0], [60.1, 310.0], [60.2, 310.0], [60.3, 310.0], [60.4, 310.0], [60.5, 310.0], [60.6, 310.0], [60.7, 310.0], [60.8, 311.0], [60.9, 311.0], [61.0, 311.0], [61.1, 311.0], [61.2, 311.0], [61.3, 311.0], [61.4, 311.0], [61.5, 312.0], [61.6, 312.0], [61.7, 312.0], [61.8, 312.0], [61.9, 312.0], [62.0, 312.0], [62.1, 312.0], [62.2, 313.0], [62.3, 313.0], [62.4, 313.0], [62.5, 313.0], [62.6, 313.0], [62.7, 313.0], [62.8, 313.0], [62.9, 313.0], [63.0, 313.0], [63.1, 314.0], [63.2, 314.0], [63.3, 314.0], [63.4, 314.0], [63.5, 314.0], [63.6, 314.0], [63.7, 314.0], [63.8, 315.0], [63.9, 315.0], [64.0, 315.0], [64.1, 315.0], [64.2, 315.0], [64.3, 315.0], [64.4, 315.0], [64.5, 316.0], [64.6, 316.0], [64.7, 316.0], [64.8, 316.0], [64.9, 316.0], [65.0, 316.0], [65.1, 317.0], [65.2, 317.0], [65.3, 317.0], [65.4, 317.0], [65.5, 318.0], [65.6, 319.0], [65.7, 319.0], [65.8, 319.0], [65.9, 319.0], [66.0, 319.0], [66.1, 319.0], [66.2, 320.0], [66.3, 320.0], [66.4, 320.0], [66.5, 320.0], [66.6, 320.0], [66.7, 320.0], [66.8, 321.0], [66.9, 321.0], [67.0, 323.0], [67.1, 323.0], [67.2, 327.0], [67.3, 327.0], [67.4, 327.0], [67.5, 327.0], [67.6, 327.0], [67.7, 331.0], [67.8, 331.0], [67.9, 331.0], [68.0, 332.0], [68.1, 332.0], [68.2, 333.0], [68.3, 335.0], [68.4, 339.0], [68.5, 339.0], [68.6, 341.0], [68.7, 342.0], [68.8, 342.0], [68.9, 343.0], [69.0, 361.0], [69.1, 366.0], [69.2, 366.0], [69.3, 371.0], [69.4, 371.0], [69.5, 377.0], [69.6, 377.0], [69.7, 380.0], [69.8, 381.0], [69.9, 381.0], [70.0, 389.0], [70.1, 389.0], [70.2, 389.0], [70.3, 389.0], [70.4, 391.0], [70.5, 391.0], [70.6, 391.0], [70.7, 394.0], [70.8, 395.0], [70.9, 396.0], [71.0, 396.0], [71.1, 398.0], [71.2, 401.0], [71.3, 401.0], [71.4, 401.0], [71.5, 403.0], [71.6, 404.0], [71.7, 404.0], [71.8, 405.0], [71.9, 408.0], [72.0, 408.0], [72.1, 409.0], [72.2, 411.0], [72.3, 414.0], [72.4, 414.0], [72.5, 426.0], [72.6, 428.0], [72.7, 428.0], [72.8, 434.0], [72.9, 436.0], [73.0, 436.0], [73.1, 436.0], [73.2, 442.0], [73.3, 442.0], [73.4, 445.0], [73.5, 445.0], [73.6, 449.0], [73.7, 450.0], [73.8, 450.0], [73.9, 456.0], [74.0, 461.0], [74.1, 462.0], [74.2, 462.0], [74.3, 464.0], [74.4, 466.0], [74.5, 466.0], [74.6, 467.0], [74.7, 469.0], [74.8, 470.0], [74.9, 470.0], [75.0, 471.0], [75.1, 472.0], [75.2, 472.0], [75.3, 472.0], [75.4, 473.0], [75.5, 475.0], [75.6, 475.0], [75.7, 476.0], [75.8, 479.0], [75.9, 479.0], [76.0, 479.0], [76.1, 482.0], [76.2, 484.0], [76.3, 484.0], [76.4, 484.0], [76.5, 485.0], [76.6, 485.0], [76.7, 485.0], [76.8, 485.0], [76.9, 492.0], [77.0, 492.0], [77.1, 497.0], [77.2, 497.0], [77.3, 501.0], [77.4, 501.0], [77.5, 503.0], [77.6, 516.0], [77.7, 516.0], [77.8, 518.0], [77.9, 519.0], [78.0, 519.0], [78.1, 519.0], [78.2, 520.0], [78.3, 528.0], [78.4, 528.0], [78.5, 530.0], [78.6, 544.0], [78.7, 545.0], [78.8, 545.0], [78.9, 545.0], [79.0, 546.0], [79.1, 546.0], [79.2, 547.0], [79.3, 556.0], [79.4, 564.0], [79.5, 564.0], [79.6, 581.0], [79.7, 581.0], [79.8, 581.0], [79.9, 590.0], [80.0, 593.0], [80.1, 593.0], [80.2, 593.0], [80.3, 595.0], [80.4, 598.0], [80.5, 598.0], [80.6, 599.0], [80.7, 599.0], [80.8, 600.0], [80.9, 600.0], [81.0, 602.0], [81.1, 603.0], [81.2, 603.0], [81.3, 603.0], [81.4, 606.0], [81.5, 606.0], [81.6, 606.0], [81.7, 607.0], [81.8, 607.0], [81.9, 609.0], [82.0, 609.0], [82.1, 612.0], [82.2, 612.0], [82.3, 612.0], [82.4, 616.0], [82.5, 617.0], [82.6, 618.0], [82.7, 618.0], [82.8, 619.0], [82.9, 619.0], [83.0, 619.0], [83.1, 620.0], [83.2, 623.0], [83.3, 626.0], [83.4, 626.0], [83.5, 628.0], [83.6, 629.0], [83.7, 629.0], [83.8, 629.0], [83.9, 631.0], [84.0, 631.0], [84.1, 631.0], [84.2, 635.0], [84.3, 640.0], [84.4, 640.0], [84.5, 647.0], [84.6, 649.0], [84.7, 661.0], [84.8, 661.0], [84.9, 664.0], [85.0, 681.0], [85.1, 688.0], [85.2, 688.0], [85.3, 692.0], [85.4, 715.0], [85.5, 715.0], [85.6, 733.0], [85.7, 737.0], [85.8, 744.0], [85.9, 744.0], [86.0, 747.0], [86.1, 760.0], [86.2, 760.0], [86.3, 764.0], [86.4, 767.0], [86.5, 767.0], [86.6, 767.0], [86.7, 768.0], [86.8, 777.0], [86.9, 777.0], [87.0, 786.0], [87.1, 799.0], [87.2, 803.0], [87.3, 803.0], [87.4, 806.0], [87.5, 806.0], [87.6, 806.0], [87.7, 810.0], [87.8, 810.0], [87.9, 850.0], [88.0, 850.0], [88.1, 916.0], [88.2, 922.0], [88.3, 922.0], [88.4, 938.0], [88.5, 963.0], [88.6, 1022.0], [88.7, 1022.0], [88.8, 1025.0], [88.9, 1045.0], [89.0, 1089.0], [89.1, 1089.0], [89.2, 1090.0], [89.3, 1094.0], [89.4, 1094.0], [89.5, 1103.0], [89.6, 1133.0], [89.7, 1133.0], [89.8, 1133.0], [89.9, 1136.0], [90.0, 1149.0], [90.1, 1149.0], [90.2, 1152.0], [90.3, 1166.0], [90.4, 1182.0], [90.5, 1182.0], [90.6, 1199.0], [90.7, 1211.0], [90.8, 1211.0], [90.9, 1221.0], [91.0, 1237.0], [91.1, 1261.0], [91.2, 1261.0], [91.3, 1270.0], [91.4, 1295.0], [91.5, 1295.0], [91.6, 1296.0], [91.7, 1302.0], [91.8, 1304.0], [91.9, 1304.0], [92.0, 1309.0], [92.1, 1311.0], [92.2, 1311.0], [92.3, 1314.0], [92.4, 1324.0], [92.5, 1327.0], [92.6, 1327.0], [92.7, 1328.0], [92.8, 1336.0], [92.9, 1339.0], [93.0, 1339.0], [93.1, 1342.0], [93.2, 1344.0], [93.3, 1344.0], [93.4, 1345.0], [93.5, 1345.0], [93.6, 1345.0], [93.7, 1345.0], [93.8, 1347.0], [93.9, 1355.0], [94.0, 1355.0], [94.1, 1362.0], [94.2, 1363.0], [94.3, 1366.0], [94.4, 1366.0], [94.5, 1366.0], [94.6, 1367.0], [94.7, 1367.0], [94.8, 1377.0], [94.9, 1378.0], [95.0, 1382.0], [95.1, 1382.0], [95.2, 1387.0], [95.3, 1388.0], [95.4, 1388.0], [95.5, 1389.0], [95.6, 1396.0], [95.7, 1405.0], [95.8, 1405.0], [95.9, 1408.0], [96.0, 1435.0], [96.1, 1435.0], [96.2, 1456.0], [96.3, 1467.0], [96.4, 1499.0], [96.5, 1499.0], [96.6, 1521.0], [96.7, 1566.0], [96.8, 1594.0], [96.9, 1594.0], [97.0, 1613.0], [97.1, 1660.0], [97.2, 1660.0], [97.3, 1680.0], [97.4, 1681.0], [97.5, 1750.0], [97.6, 1750.0], [97.7, 1765.0], [97.8, 1800.0], [97.9, 1800.0], [98.0, 1802.0], [98.1, 1809.0], [98.2, 1827.0], [98.3, 1827.0], [98.4, 1962.0], [98.5, 2050.0], [98.6, 2050.0], [98.7, 2082.0], [98.8, 2119.0], [98.9, 2125.0], [99.0, 2125.0], [99.1, 2144.0], [99.2, 2156.0], [99.3, 2156.0], [99.4, 2179.0], [99.5, 2205.0], [99.6, 2517.0], [99.7, 2517.0], [99.8, 2811.0], [99.9, 3502.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
        getOptions: function() {
            return {
                series: {
                    points: { show: false }
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimePercentiles'
                },
                xaxis: {
                    tickDecimals: 1,
                    axisLabel: "Percentiles",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Percentile value in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : %x.2 percentile was %y ms"
                },
                selection: { mode: "xy" },
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesResponseTimePercentiles"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimesPercentiles"), dataset, options);
            // setup overview
            $.plot($("#overviewResponseTimesPercentiles"), dataset, prepareOverviewOptions(options));
        }
};

/**
 * @param elementId Id of element where we display message
 */
function setEmptyGraph(elementId) {
    $(function() {
        $(elementId).text("No graph series with filter="+seriesFilter);
    });
}

// Response times percentiles
function refreshResponseTimePercentiles() {
    var infos = responseTimePercentilesInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyResponseTimePercentiles");
        return;
    }
    if (isGraph($("#flotResponseTimesPercentiles"))){
        infos.createGraph();
    } else {
        var choiceContainer = $("#choicesResponseTimePercentiles");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimesPercentiles", "#overviewResponseTimesPercentiles");
        $('#bodyResponseTimePercentiles .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
}

var responseTimeDistributionInfos = {
        data: {"result": {"minY": 1.0, "minX": 100.0, "maxY": 270.0, "series": [{"data": [[600.0, 33.0], [700.0, 13.0], [800.0, 6.0], [900.0, 4.0], [1000.0, 6.0], [1100.0, 9.0], [1200.0, 7.0], [1300.0, 29.0], [1400.0, 6.0], [1500.0, 3.0], [100.0, 35.0], [1600.0, 4.0], [1700.0, 2.0], [1800.0, 4.0], [1900.0, 1.0], [2000.0, 2.0], [2100.0, 5.0], [2200.0, 1.0], [2500.0, 1.0], [2800.0, 1.0], [200.0, 270.0], [3500.0, 1.0], [300.0, 206.0], [400.0, 44.0], [500.0, 25.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 3500.0, "title": "Response Time Distribution"}},
        getOptions: function() {
            var granularity = this.data.result.granularity;
            return {
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimeDistribution'
                },
                xaxis:{
                    axisLabel: "Response times in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of responses",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                bars : {
                    show: true,
                    barWidth: this.data.result.granularity
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: function(label, xval, yval, flotItem){
                        return yval + " responses for " + label + " were between " + xval + " and " + (xval + granularity) + " ms";
                    }
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimeDistribution"), prepareData(data.result.series, $("#choicesResponseTimeDistribution")), options);
        }

};

// Response time distribution
function refreshResponseTimeDistribution() {
    var infos = responseTimeDistributionInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyResponseTimeDistribution");
        return;
    }
    if (isGraph($("#flotResponseTimeDistribution"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesResponseTimeDistribution");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        $('#footerResponseTimeDistribution .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};


var syntheticResponseTimeDistributionInfos = {
        data: {"result": {"minY": 25.0, "minX": 0.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 555.0, "series": [{"data": [[0.0, 555.0]], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [[1.0, 138.0]], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [[2.0, 25.0]], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 2.0, "title": "Synthetic Response Times Distribution"}},
        getOptions: function() {
            return {
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendSyntheticResponseTimeDistribution'
                },
                xaxis:{
                    axisLabel: "Response times ranges",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                    tickLength:0,
                    min:-0.5,
                    max:3.5
                },
                yaxis: {
                    axisLabel: "Number of responses",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                bars : {
                    show: true,
                    align: "center",
                    barWidth: 0.25,
                    fill:.75
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: function(label, xval, yval, flotItem){
                        return yval + " " + label;
                    }
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var options = this.getOptions();
            prepareOptions(options, data);
            options.xaxis.ticks = data.result.ticks;
            $.plot($("#flotSyntheticResponseTimeDistribution"), prepareData(data.result.series, $("#choicesSyntheticResponseTimeDistribution")), options);
        }

};

// Response time distribution
function refreshSyntheticResponseTimeDistribution() {
    var infos = syntheticResponseTimeDistributionInfos;
    prepareSeries(infos.data, true);
    if (isGraph($("#flotSyntheticResponseTimeDistribution"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesSyntheticResponseTimeDistribution");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        $('#footerSyntheticResponseTimeDistribution .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var activeThreadsOverTimeInfos = {
        data: {"result": {"minY": 18.760233918128662, "minX": 1.7922189E12, "maxY": 19.494680851063833, "series": [{"data": [[1.7922189E12, 18.760233918128662], [1.79221896E12, 19.494680851063833]], "isOverall": false, "label": "Virtual Users", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79221896E12, "title": "Active Threads Over Time"}},
        getOptions: function() {
            return {
                series: {
                    stack: true,
                    lines: {
                        show: true,
                        fill: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of active threads",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 6,
                    show: true,
                    container: '#legendActiveThreadsOverTime'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                selection: {
                    mode: 'xy'
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : At %x there were %y active threads"
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesActiveThreadsOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotActiveThreadsOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewActiveThreadsOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Active Threads Over Time
function refreshActiveThreadsOverTime(fixTimestamps) {
    var infos = activeThreadsOverTimeInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 19800000);
    }
    if(isGraph($("#flotActiveThreadsOverTime"))) {
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesActiveThreadsOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotActiveThreadsOverTime", "#overviewActiveThreadsOverTime");
        $('#footerActiveThreadsOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var timeVsThreadsInfos = {
        data: {"result": {"minY": 262.8333333333333, "minX": 1.0, "maxY": 1339.0, "series": [{"data": [[8.0, 364.2], [2.0, 1339.0], [9.0, 366.5], [10.0, 558.0], [11.0, 385.5], [12.0, 467.3333333333333], [3.0, 649.0], [13.0, 470.8], [14.0, 714.5555555555555], [15.0, 262.8333333333333], [16.0, 307.0], [4.0, 623.0], [1.0, 1025.0], [17.0, 283.6666666666667], [18.0, 336.6666666666667], [19.0, 435.0], [5.0, 1107.0], [20.0, 478.0556414219474], [6.0, 455.75], [7.0, 452.1666666666667]], "isOverall": false, "label": "API Request", "isController": false}, {"data": [[19.144846796657404, 479.42479108635115]], "isOverall": false, "label": "API Request-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 20.0, "title": "Time VS Threads"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    axisLabel: "Number of active threads",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average response times in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: { noColumns: 2,show: true, container: '#legendTimeVsThreads' },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s: At %x.2 active threads, Average response time was %y.2 ms"
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesTimeVsThreads"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotTimesVsThreads"), dataset, options);
            // setup overview
            $.plot($("#overviewTimesVsThreads"), dataset, prepareOverviewOptions(options));
        }
};

// Time vs threads
function refreshTimeVsThreads(){
    var infos = timeVsThreadsInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyTimeVsThreads");
        return;
    }
    if(isGraph($("#flotTimesVsThreads"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesTimeVsThreads");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotTimesVsThreads", "#overviewTimesVsThreads");
        $('#footerTimeVsThreads .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var bytesThroughputOverTimeInfos = {
        data : {"result": {"minY": 855.0, "minX": 1.7922189E12, "maxY": 15906.95, "series": [{"data": [[1.7922189E12, 14467.166666666666], [1.79221896E12, 15906.95]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.7922189E12, 855.0], [1.79221896E12, 940.0]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79221896E12, "title": "Bytes Throughput Over Time"}},
        getOptions : function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity) ,
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Bytes / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendBytesThroughputOverTime'
                },
                selection: {
                    mode: "xy"
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y"
                }
            };
        },
        createGraph : function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesBytesThroughputOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotBytesThroughputOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewBytesThroughputOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Bytes throughput Over Time
function refreshBytesThroughputOverTime(fixTimestamps) {
    var infos = bytesThroughputOverTimeInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 19800000);
    }
    if(isGraph($("#flotBytesThroughputOverTime"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesBytesThroughputOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotBytesThroughputOverTime", "#overviewBytesThroughputOverTime");
        $('#footerBytesThroughputOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
}

var responseTimesOverTimeInfos = {
        data: {"result": {"minY": 478.9649122807016, "minX": 1.7922189E12, "maxY": 479.8430851063828, "series": [{"data": [[1.7922189E12, 478.9649122807016], [1.79221896E12, 479.8430851063828]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79221896E12, "title": "Response Time Over Time"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average response time in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimesOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Average response time was %y ms"
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesResponseTimesOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimesOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewResponseTimesOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Response Times Over Time
function refreshResponseTimeOverTime(fixTimestamps) {
    var infos = responseTimesOverTimeInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyResponseTimeOverTime");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 19800000);
    }
    if(isGraph($("#flotResponseTimesOverTime"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesResponseTimesOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimesOverTime", "#overviewResponseTimesOverTime");
        $('#footerResponseTimesOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var latenciesOverTimeInfos = {
        data: {"result": {"minY": 446.0321637426899, "minX": 1.7922189E12, "maxY": 477.792553191489, "series": [{"data": [[1.7922189E12, 446.0321637426899], [1.79221896E12, 477.792553191489]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79221896E12, "title": "Latencies Over Time"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average response latencies in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendLatenciesOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Average latency was %y ms"
                }
            };
        },
        createGraph: function () {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesLatenciesOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotLatenciesOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewLatenciesOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Latencies Over Time
function refreshLatenciesOverTime(fixTimestamps) {
    var infos = latenciesOverTimeInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyLatenciesOverTime");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 19800000);
    }
    if(isGraph($("#flotLatenciesOverTime"))) {
        infos.createGraph();
    }else {
        var choiceContainer = $("#choicesLatenciesOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotLatenciesOverTime", "#overviewLatenciesOverTime");
        $('#footerLatenciesOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var connectTimeOverTimeInfos = {
        data: {"result": {"minY": 0.0, "minX": 1.7922189E12, "maxY": 26.739766081871355, "series": [{"data": [[1.7922189E12, 26.739766081871355], [1.79221896E12, 0.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79221896E12, "title": "Connect Time Over Time"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getConnectTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average Connect Time in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendConnectTimeOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Average connect time was %y ms"
                }
            };
        },
        createGraph: function () {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesConnectTimeOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotConnectTimeOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewConnectTimeOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Connect Time Over Time
function refreshConnectTimeOverTime(fixTimestamps) {
    var infos = connectTimeOverTimeInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyConnectTimeOverTime");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 19800000);
    }
    if(isGraph($("#flotConnectTimeOverTime"))) {
        infos.createGraph();
    }else {
        var choiceContainer = $("#choicesConnectTimeOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotConnectTimeOverTime", "#overviewConnectTimeOverTime");
        $('#footerConnectTimeOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var responseTimePercentilesOverTimeInfos = {
        data: {"result": {"minY": 153.0, "minX": 1.7922189E12, "maxY": 3502.0, "series": [{"data": [[1.7922189E12, 3502.0], [1.79221896E12, 2205.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.7922189E12, 153.0], [1.79221896E12, 153.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.7922189E12, 1284.7999999999997], [1.79221896E12, 1096.7]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.7922189E12, 2329.949999999997], [1.79221896E12, 2146.76]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.7922189E12, 303.0], [1.79221896E12, 304.0]], "isOverall": false, "label": "Median", "isController": false}, {"data": [[1.7922189E12, 1407.55], [1.79221896E12, 1345.0]], "isOverall": false, "label": "95th percentile", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79221896E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true,
                        fill: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Response Time in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimePercentilesOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Response time was %y ms"
                }
            };
        },
        createGraph: function () {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesResponseTimePercentilesOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimePercentilesOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewResponseTimePercentilesOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Response Time Percentiles Over Time
function refreshResponseTimePercentilesOverTime(fixTimestamps) {
    var infos = responseTimePercentilesOverTimeInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 19800000);
    }
    if(isGraph($("#flotResponseTimePercentilesOverTime"))) {
        infos.createGraph();
    }else {
        var choiceContainer = $("#choicesResponseTimePercentilesOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimePercentilesOverTime", "#overviewResponseTimePercentilesOverTime");
        $('#footerResponseTimePercentilesOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};


var responseTimeVsRequestInfos = {
    data: {"result": {"minY": 297.0, "minX": 6.0, "maxY": 602.0, "series": [{"data": [[8.0, 300.0], [9.0, 306.0], [10.0, 301.0], [11.0, 299.5], [12.0, 305.5], [13.0, 301.0], [14.0, 302.5], [15.0, 300.5], [16.0, 310.0], [17.0, 317.5], [19.0, 302.0], [20.0, 308.0], [6.0, 602.0], [7.0, 297.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 20.0, "title": "Response Time Vs Request"}},
    getOptions: function() {
        return {
            series: {
                lines: {
                    show: false
                },
                points: {
                    show: true
                }
            },
            xaxis: {
                axisLabel: "Global number of requests per second",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            yaxis: {
                axisLabel: "Median Response Time in ms",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            legend: {
                noColumns: 2,
                show: true,
                container: '#legendResponseTimeVsRequest'
            },
            selection: {
                mode: 'xy'
            },
            grid: {
                hoverable: true // IMPORTANT! this is needed for tooltip to work
            },
            tooltip: true,
            tooltipOpts: {
                content: "%s : Median response time at %x req/s was %y ms"
            },
            colors: ["#9ACD32", "#FF6347"]
        };
    },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesResponseTimeVsRequest"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotResponseTimeVsRequest"), dataset, options);
        // setup overview
        $.plot($("#overviewResponseTimeVsRequest"), dataset, prepareOverviewOptions(options));

    }
};

// Response Time vs Request
function refreshResponseTimeVsRequest() {
    var infos = responseTimeVsRequestInfos;
    prepareSeries(infos.data);
    if (isGraph($("#flotResponseTimeVsRequest"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesResponseTimeVsRequest");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimeVsRequest", "#overviewResponseTimeVsRequest");
        $('#footerResponseRimeVsRequest .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};


var latenciesVsRequestInfos = {
    data: {"result": {"minY": 293.5, "minX": 6.0, "maxY": 602.0, "series": [{"data": [[8.0, 293.5], [9.0, 302.5], [10.0, 301.0], [11.0, 299.5], [12.0, 303.5], [13.0, 299.5], [14.0, 298.5], [15.0, 300.5], [16.0, 309.5], [17.0, 308.0], [19.0, 299.0], [20.0, 306.5], [6.0, 602.0], [7.0, 295.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 20.0, "title": "Latencies Vs Request"}},
    getOptions: function() {
        return{
            series: {
                lines: {
                    show: false
                },
                points: {
                    show: true
                }
            },
            xaxis: {
                axisLabel: "Global number of requests per second",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            yaxis: {
                axisLabel: "Median Latency in ms",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            legend: { noColumns: 2,show: true, container: '#legendLatencyVsRequest' },
            selection: {
                mode: 'xy'
            },
            grid: {
                hoverable: true // IMPORTANT! this is needed for tooltip to work
            },
            tooltip: true,
            tooltipOpts: {
                content: "%s : Median Latency time at %x req/s was %y ms"
            },
            colors: ["#9ACD32", "#FF6347"]
        };
    },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesLatencyVsRequest"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotLatenciesVsRequest"), dataset, options);
        // setup overview
        $.plot($("#overviewLatenciesVsRequest"), dataset, prepareOverviewOptions(options));
    }
};

// Latencies vs Request
function refreshLatenciesVsRequest() {
        var infos = latenciesVsRequestInfos;
        prepareSeries(infos.data);
        if(isGraph($("#flotLatenciesVsRequest"))){
            infos.createGraph();
        }else{
            var choiceContainer = $("#choicesLatencyVsRequest");
            createLegend(choiceContainer, infos);
            infos.createGraph();
            setGraphZoomable("#flotLatenciesVsRequest", "#overviewLatenciesVsRequest");
            $('#footerLatenciesVsRequest .legendColorBox > div').each(function(i){
                $(this).clone().prependTo(choiceContainer.find("li").eq(i));
            });
        }
};

var hitsPerSecondInfos = {
        data: {"result": {"minY": 5.8, "minX": 1.7922189E12, "maxY": 6.166666666666667, "series": [{"data": [[1.7922189E12, 5.8], [1.79221896E12, 6.166666666666667]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79221896E12, "title": "Hits Per Second"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of hits / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendHitsPerSecond"
                },
                selection: {
                    mode : 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y.2 hits/sec"
                }
            };
        },
        createGraph: function createGraph() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesHitsPerSecond"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotHitsPerSecond"), dataset, options);
            // setup overview
            $.plot($("#overviewHitsPerSecond"), dataset, prepareOverviewOptions(options));
        }
};

// Hits per second
function refreshHitsPerSecond(fixTimestamps) {
    var infos = hitsPerSecondInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 19800000);
    }
    if (isGraph($("#flotHitsPerSecond"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesHitsPerSecond");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotHitsPerSecond", "#overviewHitsPerSecond");
        $('#footerHitsPerSecond .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
}

var codesPerSecondInfos = {
        data: {"result": {"minY": 5.7, "minX": 1.7922189E12, "maxY": 6.266666666666667, "series": [{"data": [[1.7922189E12, 5.7], [1.79221896E12, 6.266666666666667]], "isOverall": false, "label": "200", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79221896E12, "title": "Codes Per Second"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of responses / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendCodesPerSecond"
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "Number of Response Codes %s at %x was %y.2 responses / sec"
                }
            };
        },
    createGraph: function() {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesCodesPerSecond"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotCodesPerSecond"), dataset, options);
        // setup overview
        $.plot($("#overviewCodesPerSecond"), dataset, prepareOverviewOptions(options));
    }
};

// Codes per second
function refreshCodesPerSecond(fixTimestamps) {
    var infos = codesPerSecondInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 19800000);
    }
    if(isGraph($("#flotCodesPerSecond"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesCodesPerSecond");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotCodesPerSecond", "#overviewCodesPerSecond");
        $('#footerCodesPerSecond .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var transactionsPerSecondInfos = {
        data: {"result": {"minY": 5.7, "minX": 1.7922189E12, "maxY": 6.266666666666667, "series": [{"data": [[1.7922189E12, 5.7], [1.79221896E12, 6.266666666666667]], "isOverall": false, "label": "API Request-success", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79221896E12, "title": "Transactions Per Second"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of transactions / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendTransactionsPerSecond"
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y transactions / sec"
                }
            };
        },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesTransactionsPerSecond"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotTransactionsPerSecond"), dataset, options);
        // setup overview
        $.plot($("#overviewTransactionsPerSecond"), dataset, prepareOverviewOptions(options));
    }
};

// Transactions per second
function refreshTransactionsPerSecond(fixTimestamps) {
    var infos = transactionsPerSecondInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyTransactionsPerSecond");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 19800000);
    }
    if(isGraph($("#flotTransactionsPerSecond"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesTransactionsPerSecond");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotTransactionsPerSecond", "#overviewTransactionsPerSecond");
        $('#footerTransactionsPerSecond .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var totalTPSInfos = {
        data: {"result": {"minY": 5.7, "minX": 1.7922189E12, "maxY": 6.266666666666667, "series": [{"data": [[1.7922189E12, 5.7], [1.79221896E12, 6.266666666666667]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79221896E12, "title": "Total Transactions Per Second"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of transactions / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendTotalTPS"
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y transactions / sec"
                },
                colors: ["#9ACD32", "#FF6347"]
            };
        },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesTotalTPS"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotTotalTPS"), dataset, options);
        // setup overview
        $.plot($("#overviewTotalTPS"), dataset, prepareOverviewOptions(options));
    }
};

// Total Transactions per second
function refreshTotalTPS(fixTimestamps) {
    var infos = totalTPSInfos;
    // We want to ignore seriesFilter
    prepareSeries(infos.data, false, true);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 19800000);
    }
    if(isGraph($("#flotTotalTPS"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesTotalTPS");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotTotalTPS", "#overviewTotalTPS");
        $('#footerTotalTPS .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

// Collapse the graph matching the specified DOM element depending the collapsed
// status
function collapse(elem, collapsed){
    if(collapsed){
        $(elem).parent().find(".fa-chevron-up").removeClass("fa-chevron-up").addClass("fa-chevron-down");
    } else {
        $(elem).parent().find(".fa-chevron-down").removeClass("fa-chevron-down").addClass("fa-chevron-up");
        if (elem.id == "bodyBytesThroughputOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshBytesThroughputOverTime(true);
            }
            document.location.href="#bytesThroughputOverTime";
        } else if (elem.id == "bodyLatenciesOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshLatenciesOverTime(true);
            }
            document.location.href="#latenciesOverTime";
        } else if (elem.id == "bodyCustomGraph") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshCustomGraph(true);
            }
            document.location.href="#responseCustomGraph";
        } else if (elem.id == "bodyConnectTimeOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshConnectTimeOverTime(true);
            }
            document.location.href="#connectTimeOverTime";
        } else if (elem.id == "bodyResponseTimePercentilesOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshResponseTimePercentilesOverTime(true);
            }
            document.location.href="#responseTimePercentilesOverTime";
        } else if (elem.id == "bodyResponseTimeDistribution") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshResponseTimeDistribution();
            }
            document.location.href="#responseTimeDistribution" ;
        } else if (elem.id == "bodySyntheticResponseTimeDistribution") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshSyntheticResponseTimeDistribution();
            }
            document.location.href="#syntheticResponseTimeDistribution" ;
        } else if (elem.id == "bodyActiveThreadsOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshActiveThreadsOverTime(true);
            }
            document.location.href="#activeThreadsOverTime";
        } else if (elem.id == "bodyTimeVsThreads") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshTimeVsThreads();
            }
            document.location.href="#timeVsThreads" ;
        } else if (elem.id == "bodyCodesPerSecond") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshCodesPerSecond(true);
            }
            document.location.href="#codesPerSecond";
        } else if (elem.id == "bodyTransactionsPerSecond") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshTransactionsPerSecond(true);
            }
            document.location.href="#transactionsPerSecond";
        } else if (elem.id == "bodyTotalTPS") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshTotalTPS(true);
            }
            document.location.href="#totalTPS";
        } else if (elem.id == "bodyResponseTimeVsRequest") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshResponseTimeVsRequest();
            }
            document.location.href="#responseTimeVsRequest";
        } else if (elem.id == "bodyLatenciesVsRequest") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshLatenciesVsRequest();
            }
            document.location.href="#latencyVsRequest";
        }
    }
}

/*
 * Activates or deactivates all series of the specified graph (represented by id parameter)
 * depending on checked argument.
 */
function toggleAll(id, checked){
    var placeholder = document.getElementById(id);

    var cases = $(placeholder).find(':checkbox');
    cases.prop('checked', checked);
    $(cases).parent().children().children().toggleClass("legend-disabled", !checked);

    var choiceContainer;
    if ( id == "choicesBytesThroughputOverTime"){
        choiceContainer = $("#choicesBytesThroughputOverTime");
        refreshBytesThroughputOverTime(false);
    } else if(id == "choicesResponseTimesOverTime"){
        choiceContainer = $("#choicesResponseTimesOverTime");
        refreshResponseTimeOverTime(false);
    }else if(id == "choicesResponseCustomGraph"){
        choiceContainer = $("#choicesResponseCustomGraph");
        refreshCustomGraph(false);
    } else if ( id == "choicesLatenciesOverTime"){
        choiceContainer = $("#choicesLatenciesOverTime");
        refreshLatenciesOverTime(false);
    } else if ( id == "choicesConnectTimeOverTime"){
        choiceContainer = $("#choicesConnectTimeOverTime");
        refreshConnectTimeOverTime(false);
    } else if ( id == "choicesResponseTimePercentilesOverTime"){
        choiceContainer = $("#choicesResponseTimePercentilesOverTime");
        refreshResponseTimePercentilesOverTime(false);
    } else if ( id == "choicesResponseTimePercentiles"){
        choiceContainer = $("#choicesResponseTimePercentiles");
        refreshResponseTimePercentiles();
    } else if(id == "choicesActiveThreadsOverTime"){
        choiceContainer = $("#choicesActiveThreadsOverTime");
        refreshActiveThreadsOverTime(false);
    } else if ( id == "choicesTimeVsThreads"){
        choiceContainer = $("#choicesTimeVsThreads");
        refreshTimeVsThreads();
    } else if ( id == "choicesSyntheticResponseTimeDistribution"){
        choiceContainer = $("#choicesSyntheticResponseTimeDistribution");
        refreshSyntheticResponseTimeDistribution();
    } else if ( id == "choicesResponseTimeDistribution"){
        choiceContainer = $("#choicesResponseTimeDistribution");
        refreshResponseTimeDistribution();
    } else if ( id == "choicesHitsPerSecond"){
        choiceContainer = $("#choicesHitsPerSecond");
        refreshHitsPerSecond(false);
    } else if(id == "choicesCodesPerSecond"){
        choiceContainer = $("#choicesCodesPerSecond");
        refreshCodesPerSecond(false);
    } else if ( id == "choicesTransactionsPerSecond"){
        choiceContainer = $("#choicesTransactionsPerSecond");
        refreshTransactionsPerSecond(false);
    } else if ( id == "choicesTotalTPS"){
        choiceContainer = $("#choicesTotalTPS");
        refreshTotalTPS(false);
    } else if ( id == "choicesResponseTimeVsRequest"){
        choiceContainer = $("#choicesResponseTimeVsRequest");
        refreshResponseTimeVsRequest();
    } else if ( id == "choicesLatencyVsRequest"){
        choiceContainer = $("#choicesLatencyVsRequest");
        refreshLatenciesVsRequest();
    }
    var color = checked ? "black" : "#818181";
    if(choiceContainer != null) {
        choiceContainer.find("label").each(function(){
            this.style.color = color;
        });
    }
}

