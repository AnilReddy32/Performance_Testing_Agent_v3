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
        data: {"result": {"minY": 294.0, "minX": 0.0, "maxY": 3666.0, "series": [{"data": [[0.0, 294.0], [0.1, 294.0], [0.2, 295.0], [0.3, 295.0], [0.4, 296.0], [0.5, 296.0], [0.6, 296.0], [0.7, 299.0], [0.8, 299.0], [0.9, 299.0], [1.0, 302.0], [1.1, 302.0], [1.2, 303.0], [1.3, 303.0], [1.4, 304.0], [1.5, 305.0], [1.6, 305.0], [1.7, 306.0], [1.8, 306.0], [1.9, 306.0], [2.0, 307.0], [2.1, 307.0], [2.2, 307.0], [2.3, 307.0], [2.4, 307.0], [2.5, 307.0], [2.6, 307.0], [2.7, 308.0], [2.8, 308.0], [2.9, 309.0], [3.0, 311.0], [3.1, 311.0], [3.2, 311.0], [3.3, 311.0], [3.4, 313.0], [3.5, 313.0], [3.6, 313.0], [3.7, 314.0], [3.8, 314.0], [3.9, 314.0], [4.0, 314.0], [4.1, 314.0], [4.2, 314.0], [4.3, 314.0], [4.4, 315.0], [4.5, 316.0], [4.6, 316.0], [4.7, 317.0], [4.8, 317.0], [4.9, 317.0], [5.0, 318.0], [5.1, 318.0], [5.2, 318.0], [5.3, 319.0], [5.4, 319.0], [5.5, 319.0], [5.6, 319.0], [5.7, 319.0], [5.8, 319.0], [5.9, 319.0], [6.0, 319.0], [6.1, 319.0], [6.2, 319.0], [6.3, 319.0], [6.4, 319.0], [6.5, 319.0], [6.6, 319.0], [6.7, 320.0], [6.8, 320.0], [6.9, 320.0], [7.0, 320.0], [7.1, 320.0], [7.2, 321.0], [7.3, 321.0], [7.4, 321.0], [7.5, 321.0], [7.6, 321.0], [7.7, 321.0], [7.8, 322.0], [7.9, 322.0], [8.0, 322.0], [8.1, 322.0], [8.2, 322.0], [8.3, 322.0], [8.4, 322.0], [8.5, 322.0], [8.6, 322.0], [8.7, 322.0], [8.8, 323.0], [8.9, 323.0], [9.0, 323.0], [9.1, 323.0], [9.2, 323.0], [9.3, 324.0], [9.4, 324.0], [9.5, 324.0], [9.6, 324.0], [9.7, 324.0], [9.8, 325.0], [9.9, 325.0], [10.0, 325.0], [10.1, 325.0], [10.2, 325.0], [10.3, 326.0], [10.4, 326.0], [10.5, 326.0], [10.6, 326.0], [10.7, 326.0], [10.8, 326.0], [10.9, 326.0], [11.0, 326.0], [11.1, 326.0], [11.2, 326.0], [11.3, 326.0], [11.4, 326.0], [11.5, 327.0], [11.6, 327.0], [11.7, 327.0], [11.8, 327.0], [11.9, 327.0], [12.0, 327.0], [12.1, 327.0], [12.2, 327.0], [12.3, 327.0], [12.4, 327.0], [12.5, 328.0], [12.6, 328.0], [12.7, 328.0], [12.8, 328.0], [12.9, 328.0], [13.0, 328.0], [13.1, 328.0], [13.2, 328.0], [13.3, 328.0], [13.4, 328.0], [13.5, 328.0], [13.6, 329.0], [13.7, 329.0], [13.8, 329.0], [13.9, 329.0], [14.0, 329.0], [14.1, 329.0], [14.2, 329.0], [14.3, 330.0], [14.4, 330.0], [14.5, 330.0], [14.6, 330.0], [14.7, 330.0], [14.8, 330.0], [14.9, 330.0], [15.0, 331.0], [15.1, 331.0], [15.2, 331.0], [15.3, 331.0], [15.4, 332.0], [15.5, 332.0], [15.6, 332.0], [15.7, 332.0], [15.8, 332.0], [15.9, 332.0], [16.0, 332.0], [16.1, 332.0], [16.2, 332.0], [16.3, 332.0], [16.4, 332.0], [16.5, 332.0], [16.6, 333.0], [16.7, 333.0], [16.8, 333.0], [16.9, 333.0], [17.0, 333.0], [17.1, 333.0], [17.2, 333.0], [17.3, 333.0], [17.4, 333.0], [17.5, 333.0], [17.6, 333.0], [17.7, 333.0], [17.8, 333.0], [17.9, 334.0], [18.0, 334.0], [18.1, 334.0], [18.2, 334.0], [18.3, 334.0], [18.4, 334.0], [18.5, 334.0], [18.6, 334.0], [18.7, 334.0], [18.8, 335.0], [18.9, 335.0], [19.0, 335.0], [19.1, 335.0], [19.2, 335.0], [19.3, 335.0], [19.4, 336.0], [19.5, 336.0], [19.6, 336.0], [19.7, 336.0], [19.8, 336.0], [19.9, 336.0], [20.0, 336.0], [20.1, 336.0], [20.2, 336.0], [20.3, 336.0], [20.4, 336.0], [20.5, 336.0], [20.6, 337.0], [20.7, 337.0], [20.8, 337.0], [20.9, 337.0], [21.0, 337.0], [21.1, 338.0], [21.2, 338.0], [21.3, 338.0], [21.4, 338.0], [21.5, 338.0], [21.6, 338.0], [21.7, 338.0], [21.8, 338.0], [21.9, 339.0], [22.0, 339.0], [22.1, 339.0], [22.2, 339.0], [22.3, 339.0], [22.4, 339.0], [22.5, 339.0], [22.6, 339.0], [22.7, 339.0], [22.8, 339.0], [22.9, 339.0], [23.0, 339.0], [23.1, 339.0], [23.2, 339.0], [23.3, 339.0], [23.4, 339.0], [23.5, 339.0], [23.6, 340.0], [23.7, 340.0], [23.8, 340.0], [23.9, 340.0], [24.0, 340.0], [24.1, 340.0], [24.2, 340.0], [24.3, 340.0], [24.4, 340.0], [24.5, 340.0], [24.6, 340.0], [24.7, 340.0], [24.8, 340.0], [24.9, 341.0], [25.0, 341.0], [25.1, 341.0], [25.2, 341.0], [25.3, 341.0], [25.4, 341.0], [25.5, 341.0], [25.6, 341.0], [25.7, 341.0], [25.8, 341.0], [25.9, 341.0], [26.0, 341.0], [26.1, 341.0], [26.2, 341.0], [26.3, 341.0], [26.4, 341.0], [26.5, 341.0], [26.6, 341.0], [26.7, 342.0], [26.8, 342.0], [26.9, 342.0], [27.0, 342.0], [27.1, 342.0], [27.2, 342.0], [27.3, 342.0], [27.4, 342.0], [27.5, 343.0], [27.6, 343.0], [27.7, 343.0], [27.8, 343.0], [27.9, 343.0], [28.0, 343.0], [28.1, 343.0], [28.2, 343.0], [28.3, 343.0], [28.4, 343.0], [28.5, 343.0], [28.6, 343.0], [28.7, 343.0], [28.8, 343.0], [28.9, 344.0], [29.0, 344.0], [29.1, 344.0], [29.2, 344.0], [29.3, 344.0], [29.4, 344.0], [29.5, 344.0], [29.6, 344.0], [29.7, 345.0], [29.8, 345.0], [29.9, 345.0], [30.0, 345.0], [30.1, 345.0], [30.2, 345.0], [30.3, 346.0], [30.4, 346.0], [30.5, 346.0], [30.6, 346.0], [30.7, 346.0], [30.8, 346.0], [30.9, 346.0], [31.0, 346.0], [31.1, 346.0], [31.2, 347.0], [31.3, 347.0], [31.4, 347.0], [31.5, 347.0], [31.6, 347.0], [31.7, 348.0], [31.8, 348.0], [31.9, 348.0], [32.0, 348.0], [32.1, 348.0], [32.2, 348.0], [32.3, 348.0], [32.4, 348.0], [32.5, 348.0], [32.6, 348.0], [32.7, 348.0], [32.8, 348.0], [32.9, 348.0], [33.0, 348.0], [33.1, 348.0], [33.2, 348.0], [33.3, 348.0], [33.4, 348.0], [33.5, 348.0], [33.6, 348.0], [33.7, 348.0], [33.8, 349.0], [33.9, 349.0], [34.0, 349.0], [34.1, 349.0], [34.2, 349.0], [34.3, 349.0], [34.4, 349.0], [34.5, 349.0], [34.6, 349.0], [34.7, 349.0], [34.8, 350.0], [34.9, 350.0], [35.0, 350.0], [35.1, 350.0], [35.2, 350.0], [35.3, 350.0], [35.4, 350.0], [35.5, 350.0], [35.6, 350.0], [35.7, 350.0], [35.8, 350.0], [35.9, 350.0], [36.0, 350.0], [36.1, 351.0], [36.2, 351.0], [36.3, 351.0], [36.4, 351.0], [36.5, 351.0], [36.6, 351.0], [36.7, 351.0], [36.8, 351.0], [36.9, 351.0], [37.0, 351.0], [37.1, 352.0], [37.2, 352.0], [37.3, 352.0], [37.4, 352.0], [37.5, 352.0], [37.6, 352.0], [37.7, 352.0], [37.8, 352.0], [37.9, 352.0], [38.0, 352.0], [38.1, 352.0], [38.2, 352.0], [38.3, 352.0], [38.4, 352.0], [38.5, 352.0], [38.6, 353.0], [38.7, 353.0], [38.8, 353.0], [38.9, 353.0], [39.0, 353.0], [39.1, 353.0], [39.2, 353.0], [39.3, 354.0], [39.4, 354.0], [39.5, 354.0], [39.6, 354.0], [39.7, 354.0], [39.8, 354.0], [39.9, 354.0], [40.0, 354.0], [40.1, 354.0], [40.2, 354.0], [40.3, 354.0], [40.4, 355.0], [40.5, 355.0], [40.6, 355.0], [40.7, 355.0], [40.8, 355.0], [40.9, 355.0], [41.0, 355.0], [41.1, 355.0], [41.2, 355.0], [41.3, 355.0], [41.4, 355.0], [41.5, 355.0], [41.6, 355.0], [41.7, 355.0], [41.8, 355.0], [41.9, 355.0], [42.0, 355.0], [42.1, 355.0], [42.2, 355.0], [42.3, 356.0], [42.4, 356.0], [42.5, 356.0], [42.6, 357.0], [42.7, 357.0], [42.8, 357.0], [42.9, 357.0], [43.0, 357.0], [43.1, 357.0], [43.2, 357.0], [43.3, 357.0], [43.4, 357.0], [43.5, 357.0], [43.6, 357.0], [43.7, 357.0], [43.8, 357.0], [43.9, 357.0], [44.0, 357.0], [44.1, 357.0], [44.2, 357.0], [44.3, 357.0], [44.4, 357.0], [44.5, 357.0], [44.6, 357.0], [44.7, 357.0], [44.8, 358.0], [44.9, 358.0], [45.0, 358.0], [45.1, 358.0], [45.2, 358.0], [45.3, 358.0], [45.4, 358.0], [45.5, 358.0], [45.6, 358.0], [45.7, 358.0], [45.8, 358.0], [45.9, 358.0], [46.0, 358.0], [46.1, 358.0], [46.2, 359.0], [46.3, 359.0], [46.4, 359.0], [46.5, 359.0], [46.6, 359.0], [46.7, 359.0], [46.8, 359.0], [46.9, 359.0], [47.0, 359.0], [47.1, 360.0], [47.2, 360.0], [47.3, 360.0], [47.4, 360.0], [47.5, 360.0], [47.6, 360.0], [47.7, 360.0], [47.8, 360.0], [47.9, 360.0], [48.0, 360.0], [48.1, 361.0], [48.2, 361.0], [48.3, 361.0], [48.4, 361.0], [48.5, 361.0], [48.6, 361.0], [48.7, 361.0], [48.8, 361.0], [48.9, 361.0], [49.0, 361.0], [49.1, 362.0], [49.2, 362.0], [49.3, 362.0], [49.4, 362.0], [49.5, 362.0], [49.6, 362.0], [49.7, 362.0], [49.8, 362.0], [49.9, 362.0], [50.0, 362.0], [50.1, 362.0], [50.2, 363.0], [50.3, 363.0], [50.4, 363.0], [50.5, 364.0], [50.6, 364.0], [50.7, 364.0], [50.8, 364.0], [50.9, 364.0], [51.0, 364.0], [51.1, 364.0], [51.2, 364.0], [51.3, 364.0], [51.4, 364.0], [51.5, 364.0], [51.6, 364.0], [51.7, 365.0], [51.8, 365.0], [51.9, 365.0], [52.0, 365.0], [52.1, 365.0], [52.2, 365.0], [52.3, 365.0], [52.4, 366.0], [52.5, 366.0], [52.6, 366.0], [52.7, 366.0], [52.8, 366.0], [52.9, 366.0], [53.0, 367.0], [53.1, 367.0], [53.2, 368.0], [53.3, 368.0], [53.4, 368.0], [53.5, 368.0], [53.6, 368.0], [53.7, 369.0], [53.8, 369.0], [53.9, 369.0], [54.0, 370.0], [54.1, 370.0], [54.2, 370.0], [54.3, 370.0], [54.4, 371.0], [54.5, 371.0], [54.6, 371.0], [54.7, 371.0], [54.8, 371.0], [54.9, 371.0], [55.0, 371.0], [55.1, 371.0], [55.2, 371.0], [55.3, 371.0], [55.4, 371.0], [55.5, 371.0], [55.6, 371.0], [55.7, 372.0], [55.8, 372.0], [55.9, 372.0], [56.0, 373.0], [56.1, 373.0], [56.2, 373.0], [56.3, 373.0], [56.4, 373.0], [56.5, 373.0], [56.6, 373.0], [56.7, 373.0], [56.8, 373.0], [56.9, 373.0], [57.0, 373.0], [57.1, 373.0], [57.2, 373.0], [57.3, 373.0], [57.4, 373.0], [57.5, 374.0], [57.6, 374.0], [57.7, 374.0], [57.8, 374.0], [57.9, 374.0], [58.0, 374.0], [58.1, 374.0], [58.2, 376.0], [58.3, 377.0], [58.4, 377.0], [58.5, 377.0], [58.6, 377.0], [58.7, 378.0], [58.8, 379.0], [58.9, 379.0], [59.0, 380.0], [59.1, 380.0], [59.2, 380.0], [59.3, 382.0], [59.4, 382.0], [59.5, 382.0], [59.6, 382.0], [59.7, 382.0], [59.8, 384.0], [59.9, 384.0], [60.0, 385.0], [60.1, 387.0], [60.2, 387.0], [60.3, 388.0], [60.4, 388.0], [60.5, 392.0], [60.6, 392.0], [60.7, 392.0], [60.8, 392.0], [60.9, 392.0], [61.0, 392.0], [61.1, 394.0], [61.2, 394.0], [61.3, 394.0], [61.4, 394.0], [61.5, 394.0], [61.6, 395.0], [61.7, 395.0], [61.8, 395.0], [61.9, 395.0], [62.0, 396.0], [62.1, 397.0], [62.2, 397.0], [62.3, 398.0], [62.4, 398.0], [62.5, 399.0], [62.6, 402.0], [62.7, 402.0], [62.8, 403.0], [62.9, 403.0], [63.0, 403.0], [63.1, 403.0], [63.2, 403.0], [63.3, 404.0], [63.4, 404.0], [63.5, 405.0], [63.6, 407.0], [63.7, 407.0], [63.8, 408.0], [63.9, 408.0], [64.0, 409.0], [64.1, 410.0], [64.2, 410.0], [64.3, 411.0], [64.4, 411.0], [64.5, 412.0], [64.6, 413.0], [64.7, 413.0], [64.8, 413.0], [64.9, 413.0], [65.0, 414.0], [65.1, 415.0], [65.2, 415.0], [65.3, 415.0], [65.4, 416.0], [65.5, 416.0], [65.6, 417.0], [65.7, 417.0], [65.8, 418.0], [65.9, 418.0], [66.0, 418.0], [66.1, 419.0], [66.2, 419.0], [66.3, 420.0], [66.4, 422.0], [66.5, 422.0], [66.6, 423.0], [66.7, 423.0], [66.8, 423.0], [66.9, 423.0], [67.0, 423.0], [67.1, 424.0], [67.2, 424.0], [67.3, 424.0], [67.4, 424.0], [67.5, 424.0], [67.6, 425.0], [67.7, 425.0], [67.8, 425.0], [67.9, 426.0], [68.0, 426.0], [68.1, 426.0], [68.2, 426.0], [68.3, 426.0], [68.4, 426.0], [68.5, 426.0], [68.6, 426.0], [68.7, 426.0], [68.8, 426.0], [68.9, 427.0], [69.0, 427.0], [69.1, 427.0], [69.2, 427.0], [69.3, 427.0], [69.4, 427.0], [69.5, 427.0], [69.6, 427.0], [69.7, 427.0], [69.8, 428.0], [69.9, 429.0], [70.0, 429.0], [70.1, 429.0], [70.2, 429.0], [70.3, 429.0], [70.4, 429.0], [70.5, 429.0], [70.6, 429.0], [70.7, 430.0], [70.8, 430.0], [70.9, 431.0], [71.0, 431.0], [71.1, 431.0], [71.2, 431.0], [71.3, 431.0], [71.4, 431.0], [71.5, 431.0], [71.6, 431.0], [71.7, 431.0], [71.8, 431.0], [71.9, 432.0], [72.0, 432.0], [72.1, 432.0], [72.2, 432.0], [72.3, 432.0], [72.4, 433.0], [72.5, 433.0], [72.6, 433.0], [72.7, 434.0], [72.8, 434.0], [72.9, 435.0], [73.0, 435.0], [73.1, 435.0], [73.2, 435.0], [73.3, 435.0], [73.4, 435.0], [73.5, 435.0], [73.6, 435.0], [73.7, 436.0], [73.8, 436.0], [73.9, 436.0], [74.0, 436.0], [74.1, 436.0], [74.2, 437.0], [74.3, 437.0], [74.4, 438.0], [74.5, 438.0], [74.6, 438.0], [74.7, 438.0], [74.8, 438.0], [74.9, 439.0], [75.0, 439.0], [75.1, 439.0], [75.2, 439.0], [75.3, 439.0], [75.4, 439.0], [75.5, 439.0], [75.6, 439.0], [75.7, 439.0], [75.8, 439.0], [75.9, 440.0], [76.0, 440.0], [76.1, 440.0], [76.2, 440.0], [76.3, 440.0], [76.4, 440.0], [76.5, 441.0], [76.6, 441.0], [76.7, 441.0], [76.8, 441.0], [76.9, 441.0], [77.0, 443.0], [77.1, 443.0], [77.2, 444.0], [77.3, 444.0], [77.4, 444.0], [77.5, 445.0], [77.6, 445.0], [77.7, 446.0], [77.8, 446.0], [77.9, 446.0], [78.0, 446.0], [78.1, 446.0], [78.2, 446.0], [78.3, 446.0], [78.4, 446.0], [78.5, 447.0], [78.6, 447.0], [78.7, 447.0], [78.8, 447.0], [78.9, 450.0], [79.0, 450.0], [79.1, 450.0], [79.2, 450.0], [79.3, 450.0], [79.4, 451.0], [79.5, 451.0], [79.6, 451.0], [79.7, 452.0], [79.8, 452.0], [79.9, 454.0], [80.0, 455.0], [80.1, 455.0], [80.2, 455.0], [80.3, 455.0], [80.4, 455.0], [80.5, 457.0], [80.6, 457.0], [80.7, 459.0], [80.8, 460.0], [80.9, 460.0], [81.0, 461.0], [81.1, 461.0], [81.2, 462.0], [81.3, 463.0], [81.4, 463.0], [81.5, 464.0], [81.6, 464.0], [81.7, 464.0], [81.8, 465.0], [81.9, 465.0], [82.0, 467.0], [82.1, 467.0], [82.2, 473.0], [82.3, 475.0], [82.4, 475.0], [82.5, 478.0], [82.6, 478.0], [82.7, 481.0], [82.8, 495.0], [82.9, 495.0], [83.0, 495.0], [83.1, 495.0], [83.2, 499.0], [83.3, 500.0], [83.4, 500.0], [83.5, 500.0], [83.6, 500.0], [83.7, 503.0], [83.8, 504.0], [83.9, 504.0], [84.0, 506.0], [84.1, 506.0], [84.2, 510.0], [84.3, 513.0], [84.4, 513.0], [84.5, 514.0], [84.6, 514.0], [84.7, 515.0], [84.8, 518.0], [84.9, 518.0], [85.0, 518.0], [85.1, 518.0], [85.2, 518.0], [85.3, 518.0], [85.4, 518.0], [85.5, 520.0], [85.6, 521.0], [85.7, 521.0], [85.8, 529.0], [85.9, 529.0], [86.0, 534.0], [86.1, 535.0], [86.2, 535.0], [86.3, 537.0], [86.4, 537.0], [86.5, 546.0], [86.6, 548.0], [86.7, 548.0], [86.8, 552.0], [86.9, 552.0], [87.0, 557.0], [87.1, 564.0], [87.2, 564.0], [87.3, 572.0], [87.4, 572.0], [87.5, 578.0], [87.6, 580.0], [87.7, 580.0], [87.8, 582.0], [87.9, 582.0], [88.0, 582.0], [88.1, 585.0], [88.2, 585.0], [88.3, 592.0], [88.4, 592.0], [88.5, 593.0], [88.6, 597.0], [88.7, 597.0], [88.8, 603.0], [88.9, 603.0], [89.0, 605.0], [89.1, 608.0], [89.2, 608.0], [89.3, 611.0], [89.4, 611.0], [89.5, 618.0], [89.6, 619.0], [89.7, 619.0], [89.8, 625.0], [89.9, 625.0], [90.0, 626.0], [90.1, 638.0], [90.2, 638.0], [90.3, 649.0], [90.4, 652.0], [90.5, 652.0], [90.6, 659.0], [90.7, 659.0], [90.8, 661.0], [90.9, 670.0], [91.0, 670.0], [91.1, 671.0], [91.2, 671.0], [91.3, 680.0], [91.4, 682.0], [91.5, 682.0], [91.6, 690.0], [91.7, 690.0], [91.8, 694.0], [91.9, 695.0], [92.0, 695.0], [92.1, 706.0], [92.2, 706.0], [92.3, 712.0], [92.4, 720.0], [92.5, 720.0], [92.6, 721.0], [92.7, 721.0], [92.8, 723.0], [92.9, 724.0], [93.0, 724.0], [93.1, 765.0], [93.2, 765.0], [93.3, 791.0], [93.4, 822.0], [93.5, 822.0], [93.6, 837.0], [93.7, 837.0], [93.8, 873.0], [93.9, 934.0], [94.0, 934.0], [94.1, 941.0], [94.2, 941.0], [94.3, 961.0], [94.4, 963.0], [94.5, 963.0], [94.6, 965.0], [94.7, 965.0], [94.8, 966.0], [94.9, 974.0], [95.0, 974.0], [95.1, 975.0], [95.2, 980.0], [95.3, 980.0], [95.4, 1006.0], [95.5, 1006.0], [95.6, 1008.0], [95.7, 1013.0], [95.8, 1013.0], [95.9, 1023.0], [96.0, 1023.0], [96.1, 1045.0], [96.2, 1156.0], [96.3, 1156.0], [96.4, 1175.0], [96.5, 1175.0], [96.6, 1183.0], [96.7, 1437.0], [96.8, 1437.0], [96.9, 1539.0], [97.0, 1539.0], [97.1, 1565.0], [97.2, 1589.0], [97.3, 1589.0], [97.4, 1604.0], [97.5, 1604.0], [97.6, 1699.0], [97.7, 1805.0], [97.8, 1805.0], [97.9, 1960.0], [98.0, 1960.0], [98.1, 1970.0], [98.2, 1982.0], [98.3, 1982.0], [98.4, 2017.0], [98.5, 2017.0], [98.6, 2022.0], [98.7, 2141.0], [98.8, 2141.0], [98.9, 2301.0], [99.0, 2301.0], [99.1, 2307.0], [99.2, 2633.0], [99.3, 2633.0], [99.4, 2951.0], [99.5, 2951.0], [99.6, 3396.0], [99.7, 3544.0], [99.8, 3544.0], [99.9, 3666.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
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
        data: {"result": {"minY": 1.0, "minX": 200.0, "maxY": 372.0, "series": [{"data": [[2100.0, 1.0], [2300.0, 2.0], [600.0, 20.0], [2600.0, 1.0], [700.0, 8.0], [2900.0, 1.0], [800.0, 3.0], [200.0, 6.0], [3300.0, 1.0], [3500.0, 1.0], [900.0, 9.0], [3600.0, 1.0], [1000.0, 5.0], [1100.0, 3.0], [300.0, 372.0], [1400.0, 1.0], [1500.0, 3.0], [400.0, 125.0], [1600.0, 2.0], [1800.0, 1.0], [1900.0, 3.0], [500.0, 33.0], [2000.0, 2.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 3600.0, "title": "Response Time Distribution"}},
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
        data: {"result": {"minY": 19.0, "minX": 0.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 505.0, "series": [{"data": [[0.0, 505.0]], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [[1.0, 80.0]], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [[2.0, 19.0]], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 2.0, "title": "Synthetic Response Times Distribution"}},
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
        data: {"result": {"minY": 16.0, "minX": 1.79215368E12, "maxY": 72.81500872600361, "series": [{"data": [[1.79215368E12, 72.81500872600361], [1.79215374E12, 16.0]], "isOverall": false, "label": "Virtual Users", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79215374E12, "title": "Active Threads Over Time"}},
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
        data: {"result": {"minY": 294.0, "minX": 1.0, "maxY": 1805.0, "series": [{"data": [[2.0, 341.0], [3.0, 328.0], [4.0, 422.0], [5.0, 338.0], [6.0, 335.0], [7.0, 314.0], [8.0, 451.0], [9.0, 371.0], [10.0, 361.0], [11.0, 352.0], [12.0, 528.6666666666666], [13.0, 570.6666666666666], [14.0, 358.0], [15.0, 413.0], [16.0, 341.0], [17.0, 490.5], [18.0, 345.0], [19.0, 365.5], [20.0, 445.5], [21.0, 354.5], [22.0, 667.0], [23.0, 350.0], [24.0, 613.2], [25.0, 666.5], [26.0, 661.5], [27.0, 438.0], [28.0, 527.0], [29.0, 368.5], [30.0, 335.0], [31.0, 1441.5], [32.0, 540.0], [33.0, 480.6666666666667], [34.0, 445.5], [35.0, 418.5], [36.0, 1200.5], [37.0, 518.6666666666666], [38.0, 659.6666666666666], [39.0, 321.5], [41.0, 967.0], [40.0, 368.0], [42.0, 417.75], [43.0, 381.6666666666667], [45.0, 691.5], [44.0, 294.0], [47.0, 493.5], [46.0, 344.0], [48.0, 373.0], [49.0, 487.0], [50.0, 620.25], [51.0, 650.5], [52.0, 381.6666666666667], [53.0, 455.5], [54.0, 641.6666666666666], [55.0, 619.3333333333334], [56.0, 518.6666666666666], [57.0, 404.6666666666667], [58.0, 483.6666666666667], [59.0, 360.0], [60.0, 340.5], [61.0, 480.75], [62.0, 411.5], [63.0, 439.0], [65.0, 907.0], [66.0, 500.5], [67.0, 343.0], [64.0, 314.0], [68.0, 648.0], [69.0, 519.0], [71.0, 1213.0], [70.0, 334.0], [72.0, 952.5], [73.0, 509.0], [74.0, 528.3333333333334], [75.0, 314.0], [76.0, 472.6666666666667], [77.0, 390.0], [78.0, 487.5], [79.0, 355.0], [80.0, 444.06864988558345], [1.0, 1805.0]], "isOverall": false, "label": "API Request", "isController": false}, {"data": [[69.89900662251665, 473.3841059602651]], "isOverall": false, "label": "API Request-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 80.0, "title": "Time VS Threads"}},
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
        data : {"result": {"minY": 65.61666666666666, "minX": 1.79215368E12, "maxY": 17467.183333333334, "series": [{"data": [[1.79215368E12, 17467.183333333334], [1.79215374E12, 944.8]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.79215368E12, 1212.85], [1.79215374E12, 65.61666666666666]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79215374E12, "title": "Bytes Throughput Over Time"}},
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
        data: {"result": {"minY": 469.258064516129, "minX": 1.79215368E12, "maxY": 473.6073298429321, "series": [{"data": [[1.79215368E12, 473.6073298429321], [1.79215374E12, 469.258064516129]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79215374E12, "title": "Response Time Over Time"}},
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
        data: {"result": {"minY": 468.9677419354838, "minX": 1.79215368E12, "maxY": 471.0855148342063, "series": [{"data": [[1.79215368E12, 471.0855148342063], [1.79215374E12, 468.9677419354838]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79215374E12, "title": "Latencies Over Time"}},
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
        data: {"result": {"minY": 0.0, "minX": 1.79215368E12, "maxY": 51.582897033158766, "series": [{"data": [[1.79215368E12, 51.582897033158766], [1.79215374E12, 0.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79215374E12, "title": "Connect Time Over Time"}},
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
        data: {"result": {"minY": 294.0, "minX": 1.79215368E12, "maxY": 3666.0, "series": [{"data": [[1.79215368E12, 3666.0], [1.79215374E12, 2301.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.79215368E12, 294.0], [1.79215374E12, 314.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.79215368E12, 644.6000000000003], [1.79215374E12, 447.40000000000003]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.79215368E12, 2391.759999999997], [1.79215374E12, 2301.0]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.79215368E12, 364.0], [1.79215374E12, 352.0]], "isOverall": false, "label": "Median", "isController": false}, {"data": [[1.79215368E12, 974.3], [1.79215374E12, 2003.3999999999992]], "isOverall": false, "label": "95th percentile", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79215374E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
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
    data: {"result": {"minY": 334.5, "minX": 1.0, "maxY": 1805.0, "series": [{"data": [[8.0, 359.5], [2.0, 334.5], [9.0, 361.5], [10.0, 354.0], [11.0, 369.0], [12.0, 353.5], [13.0, 380.0], [14.0, 362.0], [15.0, 429.5], [4.0, 343.5], [1.0, 1805.0], [18.0, 573.0], [20.0, 536.0], [23.0, 534.0], [6.0, 357.0], [25.0, 625.0], [7.0, 361.5]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 25.0, "title": "Response Time Vs Request"}},
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
    data: {"result": {"minY": 334.5, "minX": 1.0, "maxY": 1805.0, "series": [{"data": [[8.0, 359.5], [2.0, 334.5], [9.0, 361.0], [10.0, 354.0], [11.0, 368.5], [12.0, 348.5], [13.0, 374.0], [14.0, 360.5], [15.0, 429.5], [4.0, 343.5], [1.0, 1805.0], [18.0, 573.0], [20.0, 536.0], [23.0, 534.0], [6.0, 356.5], [25.0, 625.0], [7.0, 361.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 25.0, "title": "Latencies Vs Request"}},
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
        data: {"result": {"minY": 0.45, "minX": 1.79215368E12, "maxY": 9.616666666666667, "series": [{"data": [[1.79215368E12, 9.616666666666667], [1.79215374E12, 0.45]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79215374E12, "title": "Hits Per Second"}},
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
        data: {"result": {"minY": 0.5166666666666667, "minX": 1.79215368E12, "maxY": 9.55, "series": [{"data": [[1.79215368E12, 9.55], [1.79215374E12, 0.5166666666666667]], "isOverall": false, "label": "200", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79215374E12, "title": "Codes Per Second"}},
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
        data: {"result": {"minY": 0.5166666666666667, "minX": 1.79215368E12, "maxY": 9.55, "series": [{"data": [[1.79215368E12, 9.55], [1.79215374E12, 0.5166666666666667]], "isOverall": false, "label": "API Request-success", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79215374E12, "title": "Transactions Per Second"}},
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
        data: {"result": {"minY": 0.5166666666666667, "minX": 1.79215368E12, "maxY": 9.55, "series": [{"data": [[1.79215368E12, 9.55], [1.79215374E12, 0.5166666666666667]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79215374E12, "title": "Total Transactions Per Second"}},
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

