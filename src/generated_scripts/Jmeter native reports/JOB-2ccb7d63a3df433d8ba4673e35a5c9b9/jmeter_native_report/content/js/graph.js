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
        data: {"result": {"minY": 198.0, "minX": 0.0, "maxY": 38029.0, "series": [{"data": [[0.0, 198.0], [0.1, 198.0], [0.2, 220.0], [0.3, 224.0], [0.4, 234.0], [0.5, 245.0], [0.6, 265.0], [0.7, 267.0], [0.8, 271.0], [0.9, 281.0], [1.0, 281.0], [1.1, 292.0], [1.2, 322.0], [1.3, 338.0], [1.4, 345.0], [1.5, 346.0], [1.6, 347.0], [1.7, 349.0], [1.8, 350.0], [1.9, 350.0], [2.0, 350.0], [2.1, 352.0], [2.2, 353.0], [2.3, 353.0], [2.4, 354.0], [2.5, 355.0], [2.6, 355.0], [2.7, 355.0], [2.8, 355.0], [2.9, 356.0], [3.0, 356.0], [3.1, 357.0], [3.2, 357.0], [3.3, 357.0], [3.4, 358.0], [3.5, 358.0], [3.6, 358.0], [3.7, 358.0], [3.8, 359.0], [3.9, 359.0], [4.0, 359.0], [4.1, 360.0], [4.2, 360.0], [4.3, 360.0], [4.4, 361.0], [4.5, 361.0], [4.6, 361.0], [4.7, 361.0], [4.8, 361.0], [4.9, 362.0], [5.0, 362.0], [5.1, 362.0], [5.2, 362.0], [5.3, 363.0], [5.4, 363.0], [5.5, 363.0], [5.6, 363.0], [5.7, 363.0], [5.8, 363.0], [5.9, 363.0], [6.0, 364.0], [6.1, 364.0], [6.2, 364.0], [6.3, 364.0], [6.4, 364.0], [6.5, 364.0], [6.6, 364.0], [6.7, 365.0], [6.8, 365.0], [6.9, 365.0], [7.0, 365.0], [7.1, 365.0], [7.2, 366.0], [7.3, 366.0], [7.4, 366.0], [7.5, 366.0], [7.6, 366.0], [7.7, 366.0], [7.8, 366.0], [7.9, 366.0], [8.0, 366.0], [8.1, 366.0], [8.2, 366.0], [8.3, 366.0], [8.4, 366.0], [8.5, 367.0], [8.6, 367.0], [8.7, 367.0], [8.8, 367.0], [8.9, 367.0], [9.0, 367.0], [9.1, 367.0], [9.2, 367.0], [9.3, 367.0], [9.4, 367.0], [9.5, 368.0], [9.6, 368.0], [9.7, 368.0], [9.8, 368.0], [9.9, 368.0], [10.0, 368.0], [10.1, 368.0], [10.2, 368.0], [10.3, 368.0], [10.4, 368.0], [10.5, 368.0], [10.6, 368.0], [10.7, 368.0], [10.8, 368.0], [10.9, 368.0], [11.0, 369.0], [11.1, 369.0], [11.2, 369.0], [11.3, 369.0], [11.4, 369.0], [11.5, 369.0], [11.6, 369.0], [11.7, 369.0], [11.8, 369.0], [11.9, 370.0], [12.0, 370.0], [12.1, 370.0], [12.2, 370.0], [12.3, 370.0], [12.4, 370.0], [12.5, 370.0], [12.6, 370.0], [12.7, 370.0], [12.8, 370.0], [12.9, 370.0], [13.0, 370.0], [13.1, 371.0], [13.2, 371.0], [13.3, 371.0], [13.4, 371.0], [13.5, 371.0], [13.6, 371.0], [13.7, 371.0], [13.8, 371.0], [13.9, 371.0], [14.0, 372.0], [14.1, 372.0], [14.2, 372.0], [14.3, 372.0], [14.4, 372.0], [14.5, 372.0], [14.6, 372.0], [14.7, 372.0], [14.8, 372.0], [14.9, 372.0], [15.0, 372.0], [15.1, 372.0], [15.2, 372.0], [15.3, 372.0], [15.4, 372.0], [15.5, 372.0], [15.6, 373.0], [15.7, 373.0], [15.8, 373.0], [15.9, 373.0], [16.0, 373.0], [16.1, 373.0], [16.2, 373.0], [16.3, 373.0], [16.4, 373.0], [16.5, 373.0], [16.6, 373.0], [16.7, 373.0], [16.8, 374.0], [16.9, 374.0], [17.0, 374.0], [17.1, 374.0], [17.2, 374.0], [17.3, 374.0], [17.4, 374.0], [17.5, 374.0], [17.6, 374.0], [17.7, 374.0], [17.8, 374.0], [17.9, 374.0], [18.0, 374.0], [18.1, 374.0], [18.2, 374.0], [18.3, 374.0], [18.4, 375.0], [18.5, 375.0], [18.6, 375.0], [18.7, 375.0], [18.8, 375.0], [18.9, 375.0], [19.0, 375.0], [19.1, 375.0], [19.2, 375.0], [19.3, 376.0], [19.4, 376.0], [19.5, 376.0], [19.6, 376.0], [19.7, 376.0], [19.8, 376.0], [19.9, 376.0], [20.0, 376.0], [20.1, 376.0], [20.2, 376.0], [20.3, 376.0], [20.4, 376.0], [20.5, 376.0], [20.6, 376.0], [20.7, 376.0], [20.8, 376.0], [20.9, 376.0], [21.0, 376.0], [21.1, 377.0], [21.2, 377.0], [21.3, 377.0], [21.4, 377.0], [21.5, 377.0], [21.6, 377.0], [21.7, 377.0], [21.8, 377.0], [21.9, 377.0], [22.0, 377.0], [22.1, 377.0], [22.2, 377.0], [22.3, 377.0], [22.4, 377.0], [22.5, 378.0], [22.6, 378.0], [22.7, 378.0], [22.8, 378.0], [22.9, 378.0], [23.0, 378.0], [23.1, 378.0], [23.2, 378.0], [23.3, 378.0], [23.4, 379.0], [23.5, 379.0], [23.6, 379.0], [23.7, 379.0], [23.8, 379.0], [23.9, 379.0], [24.0, 379.0], [24.1, 379.0], [24.2, 379.0], [24.3, 379.0], [24.4, 379.0], [24.5, 379.0], [24.6, 379.0], [24.7, 379.0], [24.8, 379.0], [24.9, 379.0], [25.0, 380.0], [25.1, 380.0], [25.2, 380.0], [25.3, 380.0], [25.4, 380.0], [25.5, 380.0], [25.6, 380.0], [25.7, 380.0], [25.8, 380.0], [25.9, 380.0], [26.0, 380.0], [26.1, 380.0], [26.2, 380.0], [26.3, 380.0], [26.4, 380.0], [26.5, 380.0], [26.6, 380.0], [26.7, 381.0], [26.8, 381.0], [26.9, 381.0], [27.0, 381.0], [27.1, 381.0], [27.2, 381.0], [27.3, 381.0], [27.4, 381.0], [27.5, 381.0], [27.6, 381.0], [27.7, 381.0], [27.8, 381.0], [27.9, 381.0], [28.0, 381.0], [28.1, 381.0], [28.2, 381.0], [28.3, 382.0], [28.4, 382.0], [28.5, 382.0], [28.6, 382.0], [28.7, 382.0], [28.8, 382.0], [28.9, 382.0], [29.0, 382.0], [29.1, 382.0], [29.2, 382.0], [29.3, 382.0], [29.4, 382.0], [29.5, 382.0], [29.6, 382.0], [29.7, 382.0], [29.8, 382.0], [29.9, 382.0], [30.0, 382.0], [30.1, 382.0], [30.2, 382.0], [30.3, 382.0], [30.4, 382.0], [30.5, 382.0], [30.6, 382.0], [30.7, 382.0], [30.8, 382.0], [30.9, 383.0], [31.0, 383.0], [31.1, 383.0], [31.2, 383.0], [31.3, 383.0], [31.4, 383.0], [31.5, 383.0], [31.6, 383.0], [31.7, 383.0], [31.8, 383.0], [31.9, 383.0], [32.0, 383.0], [32.1, 383.0], [32.2, 383.0], [32.3, 383.0], [32.4, 383.0], [32.5, 383.0], [32.6, 384.0], [32.7, 384.0], [32.8, 384.0], [32.9, 384.0], [33.0, 384.0], [33.1, 384.0], [33.2, 384.0], [33.3, 384.0], [33.4, 384.0], [33.5, 384.0], [33.6, 385.0], [33.7, 385.0], [33.8, 385.0], [33.9, 385.0], [34.0, 385.0], [34.1, 385.0], [34.2, 385.0], [34.3, 385.0], [34.4, 385.0], [34.5, 385.0], [34.6, 385.0], [34.7, 385.0], [34.8, 385.0], [34.9, 385.0], [35.0, 385.0], [35.1, 386.0], [35.2, 386.0], [35.3, 386.0], [35.4, 386.0], [35.5, 386.0], [35.6, 386.0], [35.7, 386.0], [35.8, 386.0], [35.9, 386.0], [36.0, 386.0], [36.1, 386.0], [36.2, 386.0], [36.3, 386.0], [36.4, 386.0], [36.5, 386.0], [36.6, 387.0], [36.7, 387.0], [36.8, 387.0], [36.9, 387.0], [37.0, 387.0], [37.1, 387.0], [37.2, 387.0], [37.3, 387.0], [37.4, 387.0], [37.5, 387.0], [37.6, 388.0], [37.7, 388.0], [37.8, 388.0], [37.9, 388.0], [38.0, 388.0], [38.1, 388.0], [38.2, 388.0], [38.3, 388.0], [38.4, 388.0], [38.5, 388.0], [38.6, 388.0], [38.7, 388.0], [38.8, 388.0], [38.9, 388.0], [39.0, 389.0], [39.1, 389.0], [39.2, 389.0], [39.3, 389.0], [39.4, 389.0], [39.5, 389.0], [39.6, 389.0], [39.7, 389.0], [39.8, 389.0], [39.9, 390.0], [40.0, 390.0], [40.1, 390.0], [40.2, 390.0], [40.3, 390.0], [40.4, 390.0], [40.5, 390.0], [40.6, 390.0], [40.7, 390.0], [40.8, 390.0], [40.9, 390.0], [41.0, 390.0], [41.1, 390.0], [41.2, 391.0], [41.3, 391.0], [41.4, 391.0], [41.5, 391.0], [41.6, 391.0], [41.7, 391.0], [41.8, 391.0], [41.9, 391.0], [42.0, 391.0], [42.1, 391.0], [42.2, 391.0], [42.3, 391.0], [42.4, 391.0], [42.5, 391.0], [42.6, 392.0], [42.7, 392.0], [42.8, 392.0], [42.9, 392.0], [43.0, 392.0], [43.1, 392.0], [43.2, 392.0], [43.3, 392.0], [43.4, 392.0], [43.5, 392.0], [43.6, 392.0], [43.7, 392.0], [43.8, 392.0], [43.9, 392.0], [44.0, 392.0], [44.1, 392.0], [44.2, 392.0], [44.3, 392.0], [44.4, 392.0], [44.5, 392.0], [44.6, 392.0], [44.7, 392.0], [44.8, 393.0], [44.9, 393.0], [45.0, 393.0], [45.1, 393.0], [45.2, 393.0], [45.3, 393.0], [45.4, 393.0], [45.5, 393.0], [45.6, 394.0], [45.7, 394.0], [45.8, 394.0], [45.9, 394.0], [46.0, 394.0], [46.1, 394.0], [46.2, 394.0], [46.3, 394.0], [46.4, 394.0], [46.5, 394.0], [46.6, 394.0], [46.7, 394.0], [46.8, 394.0], [46.9, 394.0], [47.0, 394.0], [47.1, 394.0], [47.2, 394.0], [47.3, 395.0], [47.4, 395.0], [47.5, 395.0], [47.6, 395.0], [47.7, 395.0], [47.8, 395.0], [47.9, 395.0], [48.0, 395.0], [48.1, 395.0], [48.2, 395.0], [48.3, 395.0], [48.4, 395.0], [48.5, 395.0], [48.6, 395.0], [48.7, 395.0], [48.8, 395.0], [48.9, 395.0], [49.0, 396.0], [49.1, 396.0], [49.2, 396.0], [49.3, 396.0], [49.4, 396.0], [49.5, 396.0], [49.6, 396.0], [49.7, 396.0], [49.8, 396.0], [49.9, 397.0], [50.0, 397.0], [50.1, 397.0], [50.2, 398.0], [50.3, 398.0], [50.4, 398.0], [50.5, 398.0], [50.6, 398.0], [50.7, 398.0], [50.8, 398.0], [50.9, 398.0], [51.0, 398.0], [51.1, 398.0], [51.2, 398.0], [51.3, 399.0], [51.4, 399.0], [51.5, 399.0], [51.6, 399.0], [51.7, 399.0], [51.8, 399.0], [51.9, 399.0], [52.0, 399.0], [52.1, 399.0], [52.2, 399.0], [52.3, 399.0], [52.4, 400.0], [52.5, 400.0], [52.6, 400.0], [52.7, 400.0], [52.8, 400.0], [52.9, 400.0], [53.0, 401.0], [53.1, 401.0], [53.2, 401.0], [53.3, 401.0], [53.4, 401.0], [53.5, 401.0], [53.6, 401.0], [53.7, 401.0], [53.8, 402.0], [53.9, 402.0], [54.0, 402.0], [54.1, 402.0], [54.2, 402.0], [54.3, 402.0], [54.4, 402.0], [54.5, 402.0], [54.6, 402.0], [54.7, 403.0], [54.8, 403.0], [54.9, 403.0], [55.0, 403.0], [55.1, 403.0], [55.2, 403.0], [55.3, 403.0], [55.4, 403.0], [55.5, 403.0], [55.6, 403.0], [55.7, 404.0], [55.8, 404.0], [55.9, 404.0], [56.0, 404.0], [56.1, 405.0], [56.2, 405.0], [56.3, 405.0], [56.4, 405.0], [56.5, 405.0], [56.6, 405.0], [56.7, 405.0], [56.8, 405.0], [56.9, 406.0], [57.0, 406.0], [57.1, 406.0], [57.2, 406.0], [57.3, 406.0], [57.4, 406.0], [57.5, 407.0], [57.6, 407.0], [57.7, 407.0], [57.8, 407.0], [57.9, 407.0], [58.0, 407.0], [58.1, 408.0], [58.2, 408.0], [58.3, 408.0], [58.4, 408.0], [58.5, 408.0], [58.6, 408.0], [58.7, 408.0], [58.8, 409.0], [58.9, 409.0], [59.0, 410.0], [59.1, 410.0], [59.2, 410.0], [59.3, 411.0], [59.4, 411.0], [59.5, 411.0], [59.6, 412.0], [59.7, 412.0], [59.8, 412.0], [59.9, 412.0], [60.0, 412.0], [60.1, 413.0], [60.2, 413.0], [60.3, 413.0], [60.4, 413.0], [60.5, 414.0], [60.6, 414.0], [60.7, 414.0], [60.8, 415.0], [60.9, 415.0], [61.0, 417.0], [61.1, 417.0], [61.2, 421.0], [61.3, 421.0], [61.4, 421.0], [61.5, 422.0], [61.6, 423.0], [61.7, 424.0], [61.8, 425.0], [61.9, 425.0], [62.0, 426.0], [62.1, 437.0], [62.2, 437.0], [62.3, 440.0], [62.4, 487.0], [62.5, 757.0], [62.6, 761.0], [62.7, 776.0], [62.8, 782.0], [62.9, 783.0], [63.0, 792.0], [63.1, 792.0], [63.2, 800.0], [63.3, 803.0], [63.4, 811.0], [63.5, 830.0], [63.6, 830.0], [63.7, 833.0], [63.8, 850.0], [63.9, 927.0], [64.0, 927.0], [64.1, 933.0], [64.2, 936.0], [64.3, 942.0], [64.4, 943.0], [64.5, 945.0], [64.6, 945.0], [64.7, 946.0], [64.8, 947.0], [64.9, 947.0], [65.0, 947.0], [65.1, 948.0], [65.2, 951.0], [65.3, 952.0], [65.4, 953.0], [65.5, 953.0], [65.6, 953.0], [65.7, 954.0], [65.8, 954.0], [65.9, 954.0], [66.0, 959.0], [66.1, 962.0], [66.2, 962.0], [66.3, 962.0], [66.4, 963.0], [66.5, 963.0], [66.6, 963.0], [66.7, 963.0], [66.8, 965.0], [66.9, 965.0], [67.0, 966.0], [67.1, 967.0], [67.2, 970.0], [67.3, 970.0], [67.4, 971.0], [67.5, 972.0], [67.6, 972.0], [67.7, 972.0], [67.8, 972.0], [67.9, 973.0], [68.0, 973.0], [68.1, 975.0], [68.2, 975.0], [68.3, 975.0], [68.4, 976.0], [68.5, 976.0], [68.6, 977.0], [68.7, 978.0], [68.8, 979.0], [68.9, 979.0], [69.0, 981.0], [69.1, 982.0], [69.2, 983.0], [69.3, 983.0], [69.4, 983.0], [69.5, 983.0], [69.6, 984.0], [69.7, 984.0], [69.8, 984.0], [69.9, 985.0], [70.0, 985.0], [70.1, 987.0], [70.2, 988.0], [70.3, 988.0], [70.4, 988.0], [70.5, 988.0], [70.6, 990.0], [70.7, 992.0], [70.8, 995.0], [70.9, 995.0], [71.0, 997.0], [71.1, 1000.0], [71.2, 1000.0], [71.3, 1000.0], [71.4, 1003.0], [71.5, 1004.0], [71.6, 1005.0], [71.7, 1005.0], [71.8, 1007.0], [71.9, 1008.0], [72.0, 1010.0], [72.1, 1010.0], [72.2, 1011.0], [72.3, 1011.0], [72.4, 1012.0], [72.5, 1012.0], [72.6, 1013.0], [72.7, 1013.0], [72.8, 1016.0], [72.9, 1017.0], [73.0, 1017.0], [73.1, 1019.0], [73.2, 1019.0], [73.3, 1019.0], [73.4, 1021.0], [73.5, 1021.0], [73.6, 1023.0], [73.7, 1024.0], [73.8, 1025.0], [73.9, 1025.0], [74.0, 1025.0], [74.1, 1027.0], [74.2, 1030.0], [74.3, 1031.0], [74.4, 1034.0], [74.5, 1036.0], [74.6, 1038.0], [74.7, 1039.0], [74.8, 1039.0], [74.9, 1040.0], [75.0, 1040.0], [75.1, 1040.0], [75.2, 1041.0], [75.3, 1041.0], [75.4, 1042.0], [75.5, 1042.0], [75.6, 1054.0], [75.7, 1054.0], [75.8, 1058.0], [75.9, 1062.0], [76.0, 1065.0], [76.1, 1074.0], [76.2, 1078.0], [76.3, 1079.0], [76.4, 1081.0], [76.5, 1082.0], [76.6, 1082.0], [76.7, 1092.0], [76.8, 1094.0], [76.9, 1099.0], [77.0, 1103.0], [77.1, 1104.0], [77.2, 1104.0], [77.3, 1106.0], [77.4, 1107.0], [77.5, 1107.0], [77.6, 1115.0], [77.7, 1118.0], [77.8, 1120.0], [77.9, 1124.0], [78.0, 1128.0], [78.1, 1130.0], [78.2, 1130.0], [78.3, 1135.0], [78.4, 1135.0], [78.5, 1136.0], [78.6, 1140.0], [78.7, 1140.0], [78.8, 1141.0], [78.9, 1142.0], [79.0, 1143.0], [79.1, 1144.0], [79.2, 1145.0], [79.3, 1145.0], [79.4, 1146.0], [79.5, 1148.0], [79.6, 1148.0], [79.7, 1149.0], [79.8, 1154.0], [79.9, 1156.0], [80.0, 1156.0], [80.1, 1157.0], [80.2, 1157.0], [80.3, 1158.0], [80.4, 1161.0], [80.5, 1161.0], [80.6, 1168.0], [80.7, 1176.0], [80.8, 1189.0], [80.9, 1195.0], [81.0, 1196.0], [81.1, 1196.0], [81.2, 1200.0], [81.3, 1210.0], [81.4, 1258.0], [81.5, 1337.0], [81.6, 1346.0], [81.7, 1347.0], [81.8, 1350.0], [81.9, 1351.0], [82.0, 1351.0], [82.1, 1353.0], [82.2, 1366.0], [82.3, 1369.0], [82.4, 1369.0], [82.5, 1374.0], [82.6, 1376.0], [82.7, 1376.0], [82.8, 1378.0], [82.9, 1378.0], [83.0, 1379.0], [83.1, 1387.0], [83.2, 1396.0], [83.3, 1396.0], [83.4, 1398.0], [83.5, 1404.0], [83.6, 1406.0], [83.7, 1408.0], [83.8, 1408.0], [83.9, 1416.0], [84.0, 1417.0], [84.1, 1419.0], [84.2, 1420.0], [84.3, 1425.0], [84.4, 1426.0], [84.5, 1432.0], [84.6, 1435.0], [84.7, 1435.0], [84.8, 1466.0], [84.9, 1475.0], [85.0, 1505.0], [85.1, 1531.0], [85.2, 1531.0], [85.3, 1534.0], [85.4, 1536.0], [85.5, 1539.0], [85.6, 1539.0], [85.7, 1543.0], [85.8, 1543.0], [85.9, 1546.0], [86.0, 1550.0], [86.1, 1552.0], [86.2, 1554.0], [86.3, 1562.0], [86.4, 1562.0], [86.5, 1562.0], [86.6, 1572.0], [86.7, 1575.0], [86.8, 1579.0], [86.9, 1581.0], [87.0, 1582.0], [87.1, 1584.0], [87.2, 1594.0], [87.3, 1626.0], [87.4, 1626.0], [87.5, 1628.0], [87.6, 1648.0], [87.7, 1660.0], [87.8, 1663.0], [87.9, 1684.0], [88.0, 1691.0], [88.1, 1730.0], [88.2, 1761.0], [88.3, 1761.0], [88.4, 1771.0], [88.5, 1779.0], [88.6, 1825.0], [88.7, 1844.0], [88.8, 1851.0], [88.9, 1876.0], [89.0, 1880.0], [89.1, 1930.0], [89.2, 1930.0], [89.3, 1942.0], [89.4, 1955.0], [89.5, 1957.0], [89.6, 1960.0], [89.7, 1962.0], [89.8, 1962.0], [89.9, 1966.0], [90.0, 1971.0], [90.1, 1971.0], [90.2, 1981.0], [90.3, 1983.0], [90.4, 1984.0], [90.5, 1992.0], [90.6, 2010.0], [90.7, 2024.0], [90.8, 2025.0], [90.9, 2031.0], [91.0, 2031.0], [91.1, 2041.0], [91.2, 2044.0], [91.3, 2057.0], [91.4, 2068.0], [91.5, 2073.0], [91.6, 2082.0], [91.7, 2119.0], [91.8, 2122.0], [91.9, 2122.0], [92.0, 2129.0], [92.1, 2129.0], [92.2, 2132.0], [92.3, 2136.0], [92.4, 2179.0], [92.5, 2185.0], [92.6, 2242.0], [92.7, 2242.0], [92.8, 2242.0], [92.9, 2252.0], [93.0, 2289.0], [93.1, 2382.0], [93.2, 2439.0], [93.3, 2467.0], [93.4, 2489.0], [93.5, 2623.0], [93.6, 2630.0], [93.7, 2630.0], [93.8, 2668.0], [93.9, 2676.0], [94.0, 2681.0], [94.1, 2689.0], [94.2, 2692.0], [94.3, 2697.0], [94.4, 2708.0], [94.5, 2711.0], [94.6, 2711.0], [94.7, 2723.0], [94.8, 2786.0], [94.9, 2797.0], [95.0, 2831.0], [95.1, 2845.0], [95.2, 2863.0], [95.3, 2868.0], [95.4, 2885.0], [95.5, 2885.0], [95.6, 2901.0], [95.7, 2906.0], [95.8, 2940.0], [95.9, 2942.0], [96.0, 3059.0], [96.1, 3236.0], [96.2, 3253.0], [96.3, 3254.0], [96.4, 3254.0], [96.5, 3309.0], [96.6, 3333.0], [96.7, 3357.0], [96.8, 3543.0], [96.9, 3598.0], [97.0, 3600.0], [97.1, 3608.0], [97.2, 3703.0], [97.3, 3703.0], [97.4, 3744.0], [97.5, 3767.0], [97.6, 3772.0], [97.7, 3811.0], [97.8, 4542.0], [97.9, 4781.0], [98.0, 4848.0], [98.1, 4955.0], [98.2, 4955.0], [98.3, 5434.0], [98.4, 5434.0], [98.5, 5473.0], [98.6, 5644.0], [98.7, 5837.0], [98.8, 6022.0], [98.9, 6033.0], [99.0, 6371.0], [99.1, 6371.0], [99.2, 7546.0], [99.3, 7673.0], [99.4, 10184.0], [99.5, 10516.0], [99.6, 10621.0], [99.7, 10801.0], [99.8, 21189.0], [99.9, 38029.0], [100.0, 38029.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
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
        data: {"result": {"minY": 1.0, "minX": 100.0, "maxY": 455.0, "series": [{"data": [[700.0, 6.0], [800.0, 7.0], [900.0, 64.0], [1000.0, 52.0], [1100.0, 37.0], [1200.0, 3.0], [1300.0, 18.0], [1400.0, 13.0], [1500.0, 21.0], [1600.0, 7.0], [1700.0, 4.0], [1800.0, 5.0], [1900.0, 13.0], [2000.0, 10.0], [2100.0, 8.0], [2200.0, 4.0], [2300.0, 1.0], [2400.0, 3.0], [2600.0, 8.0], [2700.0, 5.0], [2800.0, 5.0], [2900.0, 4.0], [3000.0, 1.0], [3200.0, 3.0], [3300.0, 3.0], [3500.0, 2.0], [3700.0, 4.0], [3600.0, 2.0], [3800.0, 1.0], [4500.0, 1.0], [4700.0, 1.0], [4800.0, 1.0], [4900.0, 1.0], [5400.0, 3.0], [5600.0, 1.0], [5800.0, 1.0], [6000.0, 2.0], [6300.0, 1.0], [7600.0, 1.0], [7500.0, 1.0], [10100.0, 1.0], [10600.0, 1.0], [10500.0, 1.0], [10800.0, 1.0], [21100.0, 1.0], [100.0, 1.0], [38000.0, 1.0], [200.0, 9.0], [300.0, 455.0], [400.0, 90.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 38000.0, "title": "Response Time Distribution"}},
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
        data: {"result": {"minY": 134.0, "minX": 0.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 555.0, "series": [{"data": [[0.0, 555.0]], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [[1.0, 200.0]], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [[2.0, 134.0]], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 2.0, "title": "Synthetic Response Times Distribution"}},
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
        data: {"result": {"minY": 24.288209606986886, "minX": 1.79222106E12, "maxY": 24.292343387471, "series": [{"data": [[1.79222112E12, 24.292343387471], [1.79222106E12, 24.288209606986886]], "isOverall": false, "label": "Virtual Users", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222112E12, "title": "Active Threads Over Time"}},
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
        data: {"result": {"minY": 368.0, "minX": 1.0, "maxY": 38029.0, "series": [{"data": [[8.0, 1189.3333333333333], [2.0, 10184.0], [9.0, 3298.5], [10.0, 681.5], [11.0, 1510.6666666666667], [12.0, 625.75], [13.0, 708.0], [14.0, 368.0], [15.0, 376.5], [16.0, 794.0], [4.0, 4078.5], [1.0, 38029.0], [17.0, 1966.0], [18.0, 916.4], [19.0, 380.0], [20.0, 1612.4], [5.0, 3357.0], [21.0, 957.25], [22.0, 981.625], [23.0, 840.2], [24.0, 573.0], [6.0, 5837.0], [25.0, 903.0609013398296], [7.0, 1466.0]], "isOverall": false, "label": "API Request", "isController": false}, {"data": [[24.290213723284566, 977.1687289088869]], "isOverall": false, "label": "API Request-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 25.0, "title": "Time VS Threads"}},
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
        data : {"result": {"minY": 1005.6666666666666, "minX": 1.79222106E12, "maxY": 8457.383333333333, "series": [{"data": [[1.79222112E12, 7961.266666666666], [1.79222106E12, 8457.383333333333]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.79222112E12, 1005.6666666666666], [1.79222106E12, 1068.6666666666667]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222112E12, "title": "Bytes Throughput Over Time"}},
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
        data: {"result": {"minY": 818.6179039301311, "minX": 1.79222106E12, "maxY": 1145.6519721577724, "series": [{"data": [[1.79222112E12, 1145.6519721577724], [1.79222106E12, 818.6179039301311]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222112E12, "title": "Response Time Over Time"}},
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
        data: {"result": {"minY": 818.5196506550224, "minX": 1.79222106E12, "maxY": 1145.5893271461716, "series": [{"data": [[1.79222112E12, 1145.5893271461716], [1.79222106E12, 818.5196506550224]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222112E12, "title": "Latencies Over Time"}},
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
        data: {"result": {"minY": 0.0, "minX": 1.79222106E12, "maxY": 70.84279475982542, "series": [{"data": [[1.79222112E12, 0.0], [1.79222106E12, 70.84279475982542]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222112E12, "title": "Connect Time Over Time"}},
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
        data: {"result": {"minY": 198.0, "minX": 1.79222106E12, "maxY": 38029.0, "series": [{"data": [[1.79222112E12, 38029.0], [1.79222106E12, 7673.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.79222112E12, 234.0], [1.79222106E12, 198.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.79222112E12, 2108.8000000000006], [1.79222106E12, 1783.600000000001]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.79222112E12, 10587.400000000001], [1.79222106E12, 4087.6999999999753]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.79222112E12, 404.0], [1.79222106E12, 389.0]], "isOverall": false, "label": "Median", "isController": false}, {"data": [[1.79222112E12, 3136.599999999996], [1.79222106E12, 2692.25]], "isOverall": false, "label": "95th percentile", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222112E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
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
    data: {"result": {"minY": 381.0, "minX": 1.0, "maxY": 10184.0, "series": [{"data": [[8.0, 1074.5], [9.0, 385.0], [10.0, 400.0], [11.0, 396.0], [12.0, 396.0], [3.0, 3357.0], [13.0, 392.0], [14.0, 400.5], [15.0, 399.5], [16.0, 396.5], [1.0, 10184.0], [17.0, 395.0], [18.0, 400.0], [19.0, 390.0], [20.0, 397.5], [21.0, 381.0], [23.0, 395.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 23.0, "title": "Response Time Vs Request"}},
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
    data: {"result": {"minY": 381.0, "minX": 1.0, "maxY": 10184.0, "series": [{"data": [[8.0, 1073.0], [9.0, 385.0], [10.0, 400.0], [11.0, 396.0], [12.0, 396.0], [3.0, 3357.0], [13.0, 392.0], [14.0, 400.5], [15.0, 399.5], [16.0, 396.5], [1.0, 10184.0], [17.0, 395.0], [18.0, 400.0], [19.0, 390.0], [20.0, 397.5], [21.0, 381.0], [23.0, 395.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 23.0, "title": "Latencies Vs Request"}},
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
        data: {"result": {"minY": 6.933333333333334, "minX": 1.79222106E12, "maxY": 7.883333333333334, "series": [{"data": [[1.79222112E12, 6.933333333333334], [1.79222106E12, 7.883333333333334]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222112E12, "title": "Hits Per Second"}},
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
        data: {"result": {"minY": 7.183333333333334, "minX": 1.79222106E12, "maxY": 7.633333333333334, "series": [{"data": [[1.79222112E12, 7.183333333333334], [1.79222106E12, 7.633333333333334]], "isOverall": false, "label": "200", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222112E12, "title": "Codes Per Second"}},
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
        data: {"result": {"minY": 7.183333333333334, "minX": 1.79222106E12, "maxY": 7.633333333333334, "series": [{"data": [[1.79222112E12, 7.183333333333334], [1.79222106E12, 7.633333333333334]], "isOverall": false, "label": "API Request-success", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222112E12, "title": "Transactions Per Second"}},
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
        data: {"result": {"minY": 7.183333333333334, "minX": 1.79222106E12, "maxY": 7.633333333333334, "series": [{"data": [[1.79222112E12, 7.183333333333334], [1.79222106E12, 7.633333333333334]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222112E12, "title": "Total Transactions Per Second"}},
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

