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
        data: {"result": {"minY": 254.0, "minX": 0.0, "maxY": 889.0, "series": [{"data": [[0.0, 254.0], [0.1, 254.0], [0.2, 259.0], [0.3, 259.0], [0.4, 259.0], [0.5, 260.0], [0.6, 260.0], [0.7, 262.0], [0.8, 262.0], [0.9, 262.0], [1.0, 263.0], [1.1, 263.0], [1.2, 263.0], [1.3, 263.0], [1.4, 263.0], [1.5, 263.0], [1.6, 263.0], [1.7, 264.0], [1.8, 264.0], [1.9, 264.0], [2.0, 264.0], [2.1, 264.0], [2.2, 264.0], [2.3, 264.0], [2.4, 265.0], [2.5, 265.0], [2.6, 265.0], [2.7, 265.0], [2.8, 265.0], [2.9, 265.0], [3.0, 266.0], [3.1, 266.0], [3.2, 266.0], [3.3, 266.0], [3.4, 266.0], [3.5, 266.0], [3.6, 266.0], [3.7, 266.0], [3.8, 266.0], [3.9, 266.0], [4.0, 266.0], [4.1, 266.0], [4.2, 266.0], [4.3, 267.0], [4.4, 267.0], [4.5, 267.0], [4.6, 267.0], [4.7, 267.0], [4.8, 267.0], [4.9, 267.0], [5.0, 267.0], [5.1, 267.0], [5.2, 267.0], [5.3, 268.0], [5.4, 268.0], [5.5, 268.0], [5.6, 268.0], [5.7, 268.0], [5.8, 268.0], [5.9, 268.0], [6.0, 268.0], [6.1, 268.0], [6.2, 269.0], [6.3, 269.0], [6.4, 269.0], [6.5, 269.0], [6.6, 269.0], [6.7, 269.0], [6.8, 270.0], [6.9, 270.0], [7.0, 270.0], [7.1, 270.0], [7.2, 270.0], [7.3, 270.0], [7.4, 270.0], [7.5, 271.0], [7.6, 271.0], [7.7, 271.0], [7.8, 271.0], [7.9, 271.0], [8.0, 272.0], [8.1, 272.0], [8.2, 272.0], [8.3, 272.0], [8.4, 272.0], [8.5, 272.0], [8.6, 272.0], [8.7, 272.0], [8.8, 272.0], [8.9, 272.0], [9.0, 272.0], [9.1, 272.0], [9.2, 272.0], [9.3, 273.0], [9.4, 273.0], [9.5, 273.0], [9.6, 273.0], [9.7, 273.0], [9.8, 273.0], [9.9, 273.0], [10.0, 273.0], [10.1, 273.0], [10.2, 273.0], [10.3, 274.0], [10.4, 274.0], [10.5, 274.0], [10.6, 274.0], [10.7, 274.0], [10.8, 274.0], [10.9, 274.0], [11.0, 274.0], [11.1, 274.0], [11.2, 274.0], [11.3, 274.0], [11.4, 274.0], [11.5, 275.0], [11.6, 275.0], [11.7, 275.0], [11.8, 275.0], [11.9, 275.0], [12.0, 275.0], [12.1, 275.0], [12.2, 275.0], [12.3, 275.0], [12.4, 275.0], [12.5, 275.0], [12.6, 275.0], [12.7, 275.0], [12.8, 275.0], [12.9, 275.0], [13.0, 275.0], [13.1, 275.0], [13.2, 275.0], [13.3, 276.0], [13.4, 276.0], [13.5, 276.0], [13.6, 276.0], [13.7, 276.0], [13.8, 276.0], [13.9, 276.0], [14.0, 276.0], [14.1, 276.0], [14.2, 276.0], [14.3, 276.0], [14.4, 276.0], [14.5, 276.0], [14.6, 276.0], [14.7, 276.0], [14.8, 276.0], [14.9, 277.0], [15.0, 277.0], [15.1, 277.0], [15.2, 277.0], [15.3, 277.0], [15.4, 278.0], [15.5, 278.0], [15.6, 278.0], [15.7, 278.0], [15.8, 278.0], [15.9, 278.0], [16.0, 278.0], [16.1, 278.0], [16.2, 278.0], [16.3, 278.0], [16.4, 278.0], [16.5, 278.0], [16.6, 278.0], [16.7, 279.0], [16.8, 279.0], [16.9, 279.0], [17.0, 279.0], [17.1, 279.0], [17.2, 279.0], [17.3, 279.0], [17.4, 279.0], [17.5, 279.0], [17.6, 279.0], [17.7, 279.0], [17.8, 279.0], [17.9, 279.0], [18.0, 279.0], [18.1, 279.0], [18.2, 280.0], [18.3, 280.0], [18.4, 280.0], [18.5, 280.0], [18.6, 280.0], [18.7, 280.0], [18.8, 280.0], [18.9, 280.0], [19.0, 280.0], [19.1, 280.0], [19.2, 280.0], [19.3, 280.0], [19.4, 280.0], [19.5, 280.0], [19.6, 280.0], [19.7, 281.0], [19.8, 281.0], [19.9, 281.0], [20.0, 281.0], [20.1, 281.0], [20.2, 281.0], [20.3, 281.0], [20.4, 281.0], [20.5, 281.0], [20.6, 281.0], [20.7, 281.0], [20.8, 281.0], [20.9, 281.0], [21.0, 282.0], [21.1, 282.0], [21.2, 282.0], [21.3, 282.0], [21.4, 282.0], [21.5, 282.0], [21.6, 282.0], [21.7, 283.0], [21.8, 283.0], [21.9, 283.0], [22.0, 283.0], [22.1, 283.0], [22.2, 283.0], [22.3, 283.0], [22.4, 283.0], [22.5, 283.0], [22.6, 283.0], [22.7, 283.0], [22.8, 283.0], [22.9, 284.0], [23.0, 284.0], [23.1, 284.0], [23.2, 284.0], [23.3, 284.0], [23.4, 284.0], [23.5, 284.0], [23.6, 284.0], [23.7, 284.0], [23.8, 284.0], [23.9, 284.0], [24.0, 284.0], [24.1, 284.0], [24.2, 285.0], [24.3, 285.0], [24.4, 285.0], [24.5, 285.0], [24.6, 285.0], [24.7, 285.0], [24.8, 286.0], [24.9, 286.0], [25.0, 286.0], [25.1, 286.0], [25.2, 286.0], [25.3, 286.0], [25.4, 286.0], [25.5, 286.0], [25.6, 286.0], [25.7, 286.0], [25.8, 286.0], [25.9, 286.0], [26.0, 286.0], [26.1, 286.0], [26.2, 286.0], [26.3, 286.0], [26.4, 286.0], [26.5, 286.0], [26.6, 286.0], [26.7, 286.0], [26.8, 286.0], [26.9, 286.0], [27.0, 287.0], [27.1, 287.0], [27.2, 287.0], [27.3, 287.0], [27.4, 287.0], [27.5, 287.0], [27.6, 287.0], [27.7, 287.0], [27.8, 288.0], [27.9, 288.0], [28.0, 288.0], [28.1, 288.0], [28.2, 288.0], [28.3, 288.0], [28.4, 288.0], [28.5, 288.0], [28.6, 288.0], [28.7, 288.0], [28.8, 288.0], [28.9, 288.0], [29.0, 288.0], [29.1, 288.0], [29.2, 288.0], [29.3, 288.0], [29.4, 288.0], [29.5, 288.0], [29.6, 289.0], [29.7, 289.0], [29.8, 289.0], [29.9, 289.0], [30.0, 289.0], [30.1, 289.0], [30.2, 289.0], [30.3, 289.0], [30.4, 289.0], [30.5, 289.0], [30.6, 289.0], [30.7, 289.0], [30.8, 289.0], [30.9, 289.0], [31.0, 289.0], [31.1, 290.0], [31.2, 290.0], [31.3, 290.0], [31.4, 290.0], [31.5, 290.0], [31.6, 290.0], [31.7, 290.0], [31.8, 290.0], [31.9, 290.0], [32.0, 291.0], [32.1, 291.0], [32.2, 291.0], [32.3, 291.0], [32.4, 291.0], [32.5, 291.0], [32.6, 292.0], [32.7, 292.0], [32.8, 292.0], [32.9, 292.0], [33.0, 292.0], [33.1, 292.0], [33.2, 292.0], [33.3, 292.0], [33.4, 292.0], [33.5, 292.0], [33.6, 293.0], [33.7, 293.0], [33.8, 293.0], [33.9, 293.0], [34.0, 293.0], [34.1, 293.0], [34.2, 293.0], [34.3, 293.0], [34.4, 293.0], [34.5, 293.0], [34.6, 293.0], [34.7, 293.0], [34.8, 294.0], [34.9, 294.0], [35.0, 294.0], [35.1, 294.0], [35.2, 294.0], [35.3, 294.0], [35.4, 294.0], [35.5, 294.0], [35.6, 294.0], [35.7, 294.0], [35.8, 294.0], [35.9, 295.0], [36.0, 295.0], [36.1, 295.0], [36.2, 295.0], [36.3, 295.0], [36.4, 295.0], [36.5, 295.0], [36.6, 295.0], [36.7, 295.0], [36.8, 295.0], [36.9, 295.0], [37.0, 295.0], [37.1, 296.0], [37.2, 296.0], [37.3, 296.0], [37.4, 297.0], [37.5, 297.0], [37.6, 297.0], [37.7, 297.0], [37.8, 297.0], [37.9, 298.0], [38.0, 298.0], [38.1, 298.0], [38.2, 298.0], [38.3, 298.0], [38.4, 298.0], [38.5, 298.0], [38.6, 299.0], [38.7, 299.0], [38.8, 299.0], [38.9, 299.0], [39.0, 299.0], [39.1, 299.0], [39.2, 300.0], [39.3, 300.0], [39.4, 300.0], [39.5, 300.0], [39.6, 300.0], [39.7, 300.0], [39.8, 300.0], [39.9, 301.0], [40.0, 301.0], [40.1, 302.0], [40.2, 302.0], [40.3, 302.0], [40.4, 302.0], [40.5, 302.0], [40.6, 302.0], [40.7, 303.0], [40.8, 303.0], [40.9, 303.0], [41.0, 303.0], [41.1, 303.0], [41.2, 304.0], [41.3, 304.0], [41.4, 305.0], [41.5, 305.0], [41.6, 305.0], [41.7, 306.0], [41.8, 306.0], [41.9, 307.0], [42.0, 307.0], [42.1, 307.0], [42.2, 307.0], [42.3, 307.0], [42.4, 307.0], [42.5, 307.0], [42.6, 307.0], [42.7, 308.0], [42.8, 308.0], [42.9, 308.0], [43.0, 309.0], [43.1, 309.0], [43.2, 309.0], [43.3, 309.0], [43.4, 309.0], [43.5, 310.0], [43.6, 310.0], [43.7, 310.0], [43.8, 310.0], [43.9, 310.0], [44.0, 310.0], [44.1, 310.0], [44.2, 310.0], [44.3, 310.0], [44.4, 310.0], [44.5, 312.0], [44.6, 312.0], [44.7, 313.0], [44.8, 313.0], [44.9, 313.0], [45.0, 314.0], [45.1, 314.0], [45.2, 314.0], [45.3, 316.0], [45.4, 316.0], [45.5, 317.0], [45.6, 317.0], [45.7, 317.0], [45.8, 318.0], [45.9, 318.0], [46.0, 319.0], [46.1, 319.0], [46.2, 319.0], [46.3, 321.0], [46.4, 321.0], [46.5, 321.0], [46.6, 321.0], [46.7, 322.0], [46.8, 322.0], [46.9, 322.0], [47.0, 325.0], [47.1, 325.0], [47.2, 326.0], [47.3, 326.0], [47.4, 326.0], [47.5, 328.0], [47.6, 328.0], [47.7, 328.0], [47.8, 329.0], [47.9, 329.0], [48.0, 329.0], [48.1, 329.0], [48.2, 329.0], [48.3, 330.0], [48.4, 330.0], [48.5, 330.0], [48.6, 331.0], [48.7, 331.0], [48.8, 331.0], [48.9, 331.0], [49.0, 331.0], [49.1, 332.0], [49.2, 332.0], [49.3, 333.0], [49.4, 333.0], [49.5, 333.0], [49.6, 334.0], [49.7, 334.0], [49.8, 334.0], [49.9, 334.0], [50.0, 334.0], [50.1, 334.0], [50.2, 334.0], [50.3, 334.0], [50.4, 334.0], [50.5, 335.0], [50.6, 336.0], [50.7, 336.0], [50.8, 336.0], [50.9, 336.0], [51.0, 337.0], [51.1, 337.0], [51.2, 337.0], [51.3, 338.0], [51.4, 338.0], [51.5, 338.0], [51.6, 338.0], [51.7, 338.0], [51.8, 338.0], [51.9, 338.0], [52.0, 338.0], [52.1, 338.0], [52.2, 338.0], [52.3, 339.0], [52.4, 340.0], [52.5, 340.0], [52.6, 340.0], [52.7, 340.0], [52.8, 340.0], [52.9, 341.0], [53.0, 341.0], [53.1, 341.0], [53.2, 341.0], [53.3, 341.0], [53.4, 341.0], [53.5, 341.0], [53.6, 341.0], [53.7, 341.0], [53.8, 342.0], [53.9, 343.0], [54.0, 343.0], [54.1, 343.0], [54.2, 343.0], [54.3, 344.0], [54.4, 344.0], [54.5, 344.0], [54.6, 344.0], [54.7, 344.0], [54.8, 344.0], [54.9, 344.0], [55.0, 344.0], [55.1, 345.0], [55.2, 345.0], [55.3, 346.0], [55.4, 346.0], [55.5, 346.0], [55.6, 346.0], [55.7, 346.0], [55.8, 347.0], [55.9, 347.0], [56.0, 347.0], [56.1, 347.0], [56.2, 347.0], [56.3, 347.0], [56.4, 347.0], [56.5, 347.0], [56.6, 347.0], [56.7, 348.0], [56.8, 348.0], [56.9, 348.0], [57.0, 348.0], [57.1, 348.0], [57.2, 349.0], [57.3, 349.0], [57.4, 349.0], [57.5, 349.0], [57.6, 349.0], [57.7, 349.0], [57.8, 349.0], [57.9, 349.0], [58.0, 349.0], [58.1, 350.0], [58.2, 350.0], [58.3, 350.0], [58.4, 350.0], [58.5, 350.0], [58.6, 350.0], [58.7, 351.0], [58.8, 351.0], [58.9, 351.0], [59.0, 351.0], [59.1, 351.0], [59.2, 351.0], [59.3, 351.0], [59.4, 352.0], [59.5, 352.0], [59.6, 352.0], [59.7, 352.0], [59.8, 352.0], [59.9, 353.0], [60.0, 353.0], [60.1, 353.0], [60.2, 353.0], [60.3, 353.0], [60.4, 354.0], [60.5, 354.0], [60.6, 354.0], [60.7, 355.0], [60.8, 355.0], [60.9, 355.0], [61.0, 355.0], [61.1, 355.0], [61.2, 356.0], [61.3, 356.0], [61.4, 356.0], [61.5, 356.0], [61.6, 356.0], [61.7, 356.0], [61.8, 356.0], [61.9, 356.0], [62.0, 358.0], [62.1, 358.0], [62.2, 358.0], [62.3, 358.0], [62.4, 359.0], [62.5, 359.0], [62.6, 359.0], [62.7, 359.0], [62.8, 359.0], [62.9, 361.0], [63.0, 361.0], [63.1, 361.0], [63.2, 362.0], [63.3, 362.0], [63.4, 363.0], [63.5, 363.0], [63.6, 363.0], [63.7, 363.0], [63.8, 363.0], [63.9, 364.0], [64.0, 364.0], [64.1, 364.0], [64.2, 365.0], [64.3, 365.0], [64.4, 365.0], [64.5, 365.0], [64.6, 365.0], [64.7, 366.0], [64.8, 367.0], [64.9, 367.0], [65.0, 367.0], [65.1, 367.0], [65.2, 370.0], [65.3, 370.0], [65.4, 370.0], [65.5, 371.0], [65.6, 371.0], [65.7, 371.0], [65.8, 372.0], [65.9, 372.0], [66.0, 372.0], [66.1, 372.0], [66.2, 372.0], [66.3, 373.0], [66.4, 373.0], [66.5, 373.0], [66.6, 373.0], [66.7, 373.0], [66.8, 373.0], [66.9, 373.0], [67.0, 373.0], [67.1, 373.0], [67.2, 374.0], [67.3, 375.0], [67.4, 375.0], [67.5, 375.0], [67.6, 375.0], [67.7, 376.0], [67.8, 377.0], [67.9, 377.0], [68.0, 377.0], [68.1, 377.0], [68.2, 377.0], [68.3, 378.0], [68.4, 378.0], [68.5, 378.0], [68.6, 379.0], [68.7, 379.0], [68.8, 379.0], [68.9, 379.0], [69.0, 380.0], [69.1, 380.0], [69.2, 380.0], [69.3, 380.0], [69.4, 380.0], [69.5, 381.0], [69.6, 381.0], [69.7, 381.0], [69.8, 381.0], [69.9, 381.0], [70.0, 381.0], [70.1, 381.0], [70.2, 381.0], [70.3, 382.0], [70.4, 382.0], [70.5, 383.0], [70.6, 383.0], [70.7, 383.0], [70.8, 383.0], [70.9, 383.0], [71.0, 384.0], [71.1, 384.0], [71.2, 384.0], [71.3, 384.0], [71.4, 384.0], [71.5, 384.0], [71.6, 384.0], [71.7, 384.0], [71.8, 385.0], [71.9, 385.0], [72.0, 385.0], [72.1, 385.0], [72.2, 385.0], [72.3, 386.0], [72.4, 386.0], [72.5, 386.0], [72.6, 386.0], [72.7, 386.0], [72.8, 387.0], [72.9, 387.0], [73.0, 387.0], [73.1, 387.0], [73.2, 387.0], [73.3, 388.0], [73.4, 388.0], [73.5, 388.0], [73.6, 389.0], [73.7, 389.0], [73.8, 389.0], [73.9, 390.0], [74.0, 390.0], [74.1, 391.0], [74.2, 391.0], [74.3, 392.0], [74.4, 392.0], [74.5, 392.0], [74.6, 392.0], [74.7, 392.0], [74.8, 393.0], [74.9, 393.0], [75.0, 393.0], [75.1, 394.0], [75.2, 394.0], [75.3, 394.0], [75.4, 394.0], [75.5, 394.0], [75.6, 395.0], [75.7, 395.0], [75.8, 395.0], [75.9, 395.0], [76.0, 395.0], [76.1, 396.0], [76.2, 396.0], [76.3, 396.0], [76.4, 396.0], [76.5, 396.0], [76.6, 398.0], [76.7, 399.0], [76.8, 399.0], [76.9, 400.0], [77.0, 400.0], [77.1, 400.0], [77.2, 400.0], [77.3, 400.0], [77.4, 400.0], [77.5, 400.0], [77.6, 401.0], [77.7, 402.0], [77.8, 402.0], [77.9, 403.0], [78.0, 403.0], [78.1, 403.0], [78.2, 405.0], [78.3, 405.0], [78.4, 406.0], [78.5, 406.0], [78.6, 408.0], [78.7, 409.0], [78.8, 409.0], [78.9, 409.0], [79.0, 409.0], [79.1, 410.0], [79.2, 410.0], [79.3, 410.0], [79.4, 411.0], [79.5, 411.0], [79.6, 411.0], [79.7, 412.0], [79.8, 412.0], [79.9, 412.0], [80.0, 412.0], [80.1, 413.0], [80.2, 414.0], [80.3, 414.0], [80.4, 414.0], [80.5, 414.0], [80.6, 414.0], [80.7, 415.0], [80.8, 415.0], [80.9, 415.0], [81.0, 418.0], [81.1, 418.0], [81.2, 419.0], [81.3, 419.0], [81.4, 421.0], [81.5, 421.0], [81.6, 421.0], [81.7, 423.0], [81.8, 423.0], [81.9, 424.0], [82.0, 425.0], [82.1, 425.0], [82.2, 428.0], [82.3, 428.0], [82.4, 430.0], [82.5, 431.0], [82.6, 431.0], [82.7, 434.0], [82.8, 434.0], [82.9, 434.0], [83.0, 436.0], [83.1, 436.0], [83.2, 437.0], [83.3, 437.0], [83.4, 439.0], [83.5, 441.0], [83.6, 441.0], [83.7, 443.0], [83.8, 443.0], [83.9, 444.0], [84.0, 445.0], [84.1, 445.0], [84.2, 445.0], [84.3, 445.0], [84.4, 445.0], [84.5, 446.0], [84.6, 446.0], [84.7, 447.0], [84.8, 447.0], [84.9, 447.0], [85.0, 449.0], [85.1, 449.0], [85.2, 450.0], [85.3, 450.0], [85.4, 450.0], [85.5, 450.0], [85.6, 450.0], [85.7, 451.0], [85.8, 456.0], [85.9, 456.0], [86.0, 457.0], [86.1, 457.0], [86.2, 459.0], [86.3, 460.0], [86.4, 460.0], [86.5, 463.0], [86.6, 463.0], [86.7, 468.0], [86.8, 470.0], [86.9, 470.0], [87.0, 471.0], [87.1, 471.0], [87.2, 471.0], [87.3, 471.0], [87.4, 471.0], [87.5, 473.0], [87.6, 473.0], [87.7, 475.0], [87.8, 476.0], [87.9, 476.0], [88.0, 476.0], [88.1, 477.0], [88.2, 477.0], [88.3, 478.0], [88.4, 478.0], [88.5, 478.0], [88.6, 478.0], [88.7, 478.0], [88.8, 479.0], [88.9, 479.0], [89.0, 479.0], [89.1, 480.0], [89.2, 480.0], [89.3, 480.0], [89.4, 480.0], [89.5, 481.0], [89.6, 483.0], [89.7, 483.0], [89.8, 486.0], [89.9, 486.0], [90.0, 486.0], [90.1, 486.0], [90.2, 486.0], [90.3, 487.0], [90.4, 487.0], [90.5, 488.0], [90.6, 489.0], [90.7, 489.0], [90.8, 490.0], [90.9, 490.0], [91.0, 491.0], [91.1, 493.0], [91.2, 493.0], [91.3, 496.0], [91.4, 496.0], [91.5, 497.0], [91.6, 497.0], [91.7, 497.0], [91.8, 510.0], [91.9, 510.0], [92.0, 516.0], [92.1, 518.0], [92.2, 518.0], [92.3, 522.0], [92.4, 523.0], [92.5, 523.0], [92.6, 524.0], [92.7, 524.0], [92.8, 526.0], [92.9, 530.0], [93.0, 530.0], [93.1, 541.0], [93.2, 541.0], [93.3, 569.0], [93.4, 575.0], [93.5, 575.0], [93.6, 582.0], [93.7, 582.0], [93.8, 584.0], [93.9, 594.0], [94.0, 594.0], [94.1, 594.0], [94.2, 594.0], [94.3, 595.0], [94.4, 598.0], [94.5, 598.0], [94.6, 600.0], [94.7, 600.0], [94.8, 600.0], [94.9, 601.0], [95.0, 601.0], [95.1, 604.0], [95.2, 604.0], [95.3, 606.0], [95.4, 608.0], [95.5, 608.0], [95.6, 608.0], [95.7, 608.0], [95.8, 610.0], [95.9, 620.0], [96.0, 620.0], [96.1, 629.0], [96.2, 640.0], [96.3, 640.0], [96.4, 645.0], [96.5, 645.0], [96.6, 657.0], [96.7, 659.0], [96.8, 659.0], [96.9, 691.0], [97.0, 691.0], [97.1, 702.0], [97.2, 704.0], [97.3, 704.0], [97.4, 709.0], [97.5, 709.0], [97.6, 711.0], [97.7, 712.0], [97.8, 712.0], [97.9, 713.0], [98.0, 713.0], [98.1, 717.0], [98.2, 732.0], [98.3, 732.0], [98.4, 733.0], [98.5, 733.0], [98.6, 735.0], [98.7, 742.0], [98.8, 742.0], [98.9, 745.0], [99.0, 745.0], [99.1, 754.0], [99.2, 755.0], [99.3, 755.0], [99.4, 758.0], [99.5, 758.0], [99.6, 797.0], [99.7, 820.0], [99.8, 820.0], [99.9, 889.0], [100.0, 889.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
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
        data: {"result": {"minY": 2.0, "minX": 200.0, "maxY": 237.0, "series": [{"data": [[600.0, 15.0], [300.0, 228.0], [700.0, 16.0], [400.0, 90.0], [200.0, 237.0], [800.0, 2.0], [500.0, 17.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 800.0, "title": "Response Time Distribution"}},
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
        data: {"result": {"minY": 50.0, "minX": 0.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 555.0, "series": [{"data": [[0.0, 555.0]], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [[1.0, 50.0]], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 1.0, "title": "Synthetic Response Times Distribution"}},
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
        data: {"result": {"minY": 49.657657657657666, "minX": 1.79222034E12, "maxY": 73.60526315789467, "series": [{"data": [[1.79222034E12, 49.657657657657666], [1.7922204E12, 73.60526315789467]], "isOverall": false, "label": "Virtual Users", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.7922204E12, "title": "Active Threads Over Time"}},
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
        data: {"result": {"minY": 270.3333333333333, "minX": 1.0, "maxY": 614.0, "series": [{"data": [[2.0, 418.0], [3.0, 331.0], [4.0, 322.0], [5.0, 292.0], [6.0, 298.0], [7.0, 298.0], [8.0, 288.0], [9.0, 384.0], [10.0, 284.0], [11.0, 506.4], [12.0, 379.0], [13.0, 382.0], [14.0, 445.0], [15.0, 404.0], [16.0, 344.75], [17.0, 349.0], [18.0, 521.0], [19.0, 421.0], [20.0, 349.0], [21.0, 482.3333333333333], [22.0, 538.0], [23.0, 485.0], [24.0, 417.0], [25.0, 387.0], [26.0, 410.0], [27.0, 298.0], [28.0, 384.5], [29.0, 488.0], [30.0, 284.0], [31.0, 356.5], [32.0, 392.5], [33.0, 586.25], [34.0, 394.5], [35.0, 409.0], [37.0, 364.6666666666667], [36.0, 343.0], [38.0, 522.5], [39.0, 319.5], [40.0, 466.0], [41.0, 388.5], [42.0, 361.0], [43.0, 475.3333333333333], [44.0, 392.6666666666667], [45.0, 295.0], [46.0, 471.3333333333333], [47.0, 554.6666666666666], [49.0, 427.0], [48.0, 285.0], [51.0, 442.0], [50.0, 410.0], [52.0, 483.0], [53.0, 378.0], [55.0, 487.6], [54.0, 396.0], [56.0, 369.3333333333333], [57.0, 415.5], [59.0, 331.5], [58.0, 381.0], [60.0, 343.6666666666667], [61.0, 449.5], [63.0, 507.3333333333333], [62.0, 271.0], [64.0, 403.5], [65.0, 531.5], [66.0, 358.5], [67.0, 295.0], [68.0, 426.5], [69.0, 270.3333333333333], [71.0, 546.3333333333334], [70.0, 338.0], [72.0, 530.6666666666666], [73.0, 474.0], [74.0, 484.5], [75.0, 356.0], [76.0, 429.25], [77.0, 614.0], [79.0, 582.0], [78.0, 394.0], [80.0, 336.0346420323323], [1.0, 569.0]], "isOverall": false, "label": "API Request", "isController": false}, {"data": [[69.21157024793395, 361.33553719008256]], "isOverall": false, "label": "API Request-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 80.0, "title": "Time VS Threads"}},
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
        data : {"result": {"minY": 234.95, "minX": 1.79222034E12, "maxY": 15062.0, "series": [{"data": [[1.79222034E12, 3384.7833333333333], [1.7922204E12, 15062.0]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.79222034E12, 234.95], [1.7922204E12, 1045.6333333333334]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.7922204E12, "title": "Bytes Throughput Over Time"}},
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
        data: {"result": {"minY": 332.5121457489877, "minX": 1.79222034E12, "maxY": 489.61261261261257, "series": [{"data": [[1.79222034E12, 489.61261261261257], [1.7922204E12, 332.5121457489877]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.7922204E12, "title": "Response Time Over Time"}},
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
        data: {"result": {"minY": 329.42307692307696, "minX": 1.79222034E12, "maxY": 489.21621621621625, "series": [{"data": [[1.79222034E12, 489.21621621621625], [1.7922204E12, 329.42307692307696]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.7922204E12, "title": "Latencies Over Time"}},
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
        data: {"result": {"minY": 0.0, "minX": 1.79222034E12, "maxY": 170.44144144144138, "series": [{"data": [[1.79222034E12, 170.44144144144138], [1.7922204E12, 0.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.7922204E12, "title": "Connect Time Over Time"}},
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
        data: {"result": {"minY": 254.0, "minX": 1.79222034E12, "maxY": 889.0, "series": [{"data": [[1.79222034E12, 889.0], [1.7922204E12, 797.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.79222034E12, 263.0], [1.7922204E12, 254.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.79222034E12, 712.8], [1.7922204E12, 407.0]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.79222034E12, 880.7199999999997], [1.7922204E12, 640.9500000000003]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.79222034E12, 480.0], [1.7922204E12, 313.0]], "isOverall": false, "label": "Median", "isController": false}, {"data": [[1.79222034E12, 748.5999999999999], [1.7922204E12, 434.5]], "isOverall": false, "label": "95th percentile", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.7922204E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
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
    data: {"result": {"minY": 305.5, "minX": 4.0, "maxY": 488.0, "series": [{"data": [[8.0, 311.5], [9.0, 310.0], [10.0, 308.0], [11.0, 329.0], [16.0, 452.0], [4.0, 326.5], [18.0, 473.5], [19.0, 488.0], [5.0, 337.0], [23.0, 487.0], [24.0, 486.0], [6.0, 305.5], [7.0, 310.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 24.0, "title": "Response Time Vs Request"}},
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
    data: {"result": {"minY": 305.5, "minX": 4.0, "maxY": 488.0, "series": [{"data": [[8.0, 310.5], [9.0, 310.0], [10.0, 308.0], [11.0, 323.5], [16.0, 452.0], [4.0, 324.0], [18.0, 473.5], [19.0, 488.0], [5.0, 337.0], [23.0, 487.0], [24.0, 483.0], [6.0, 305.5], [7.0, 305.5]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 24.0, "title": "Latencies Vs Request"}},
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
        data: {"result": {"minY": 1.8666666666666667, "minX": 1.79222034E12, "maxY": 8.216666666666667, "series": [{"data": [[1.79222034E12, 1.8666666666666667], [1.7922204E12, 8.216666666666667]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.7922204E12, "title": "Hits Per Second"}},
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
        data: {"result": {"minY": 1.85, "minX": 1.79222034E12, "maxY": 8.233333333333333, "series": [{"data": [[1.79222034E12, 1.85], [1.7922204E12, 8.233333333333333]], "isOverall": false, "label": "200", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.7922204E12, "title": "Codes Per Second"}},
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
        data: {"result": {"minY": 1.85, "minX": 1.79222034E12, "maxY": 8.233333333333333, "series": [{"data": [[1.79222034E12, 1.85], [1.7922204E12, 8.233333333333333]], "isOverall": false, "label": "API Request-success", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.7922204E12, "title": "Transactions Per Second"}},
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
        data: {"result": {"minY": 1.85, "minX": 1.79222034E12, "maxY": 8.233333333333333, "series": [{"data": [[1.79222034E12, 1.85], [1.7922204E12, 8.233333333333333]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.7922204E12, "title": "Total Transactions Per Second"}},
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

