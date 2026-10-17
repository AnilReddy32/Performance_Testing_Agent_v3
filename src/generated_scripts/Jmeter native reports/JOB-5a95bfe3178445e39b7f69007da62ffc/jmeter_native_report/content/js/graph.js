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
        data: {"result": {"minY": 259.0, "minX": 0.0, "maxY": 832.0, "series": [{"data": [[0.0, 259.0], [0.1, 259.0], [0.2, 259.0], [0.3, 259.0], [0.4, 261.0], [0.5, 261.0], [0.6, 261.0], [0.7, 261.0], [0.8, 261.0], [0.9, 262.0], [1.0, 262.0], [1.1, 262.0], [1.2, 262.0], [1.3, 262.0], [1.4, 262.0], [1.5, 262.0], [1.6, 262.0], [1.7, 264.0], [1.8, 264.0], [1.9, 264.0], [2.0, 265.0], [2.1, 265.0], [2.2, 265.0], [2.3, 265.0], [2.4, 266.0], [2.5, 266.0], [2.6, 266.0], [2.7, 266.0], [2.8, 266.0], [2.9, 266.0], [3.0, 267.0], [3.1, 267.0], [3.2, 267.0], [3.3, 267.0], [3.4, 267.0], [3.5, 267.0], [3.6, 267.0], [3.7, 267.0], [3.8, 267.0], [3.9, 268.0], [4.0, 268.0], [4.1, 268.0], [4.2, 268.0], [4.3, 268.0], [4.4, 268.0], [4.5, 268.0], [4.6, 268.0], [4.7, 269.0], [4.8, 269.0], [4.9, 269.0], [5.0, 269.0], [5.1, 269.0], [5.2, 269.0], [5.3, 269.0], [5.4, 269.0], [5.5, 270.0], [5.6, 270.0], [5.7, 270.0], [5.8, 270.0], [5.9, 270.0], [6.0, 270.0], [6.1, 270.0], [6.2, 270.0], [6.3, 270.0], [6.4, 270.0], [6.5, 270.0], [6.6, 270.0], [6.7, 271.0], [6.8, 271.0], [6.9, 271.0], [7.0, 271.0], [7.1, 271.0], [7.2, 271.0], [7.3, 271.0], [7.4, 271.0], [7.5, 271.0], [7.6, 271.0], [7.7, 271.0], [7.8, 271.0], [7.9, 271.0], [8.0, 271.0], [8.1, 271.0], [8.2, 272.0], [8.3, 272.0], [8.4, 272.0], [8.5, 272.0], [8.6, 272.0], [8.7, 272.0], [8.8, 273.0], [8.9, 273.0], [9.0, 273.0], [9.1, 273.0], [9.2, 273.0], [9.3, 273.0], [9.4, 273.0], [9.5, 273.0], [9.6, 273.0], [9.7, 273.0], [9.8, 273.0], [9.9, 273.0], [10.0, 273.0], [10.1, 273.0], [10.2, 273.0], [10.3, 274.0], [10.4, 274.0], [10.5, 274.0], [10.6, 274.0], [10.7, 274.0], [10.8, 274.0], [10.9, 274.0], [11.0, 275.0], [11.1, 275.0], [11.2, 275.0], [11.3, 275.0], [11.4, 275.0], [11.5, 275.0], [11.6, 275.0], [11.7, 275.0], [11.8, 275.0], [11.9, 275.0], [12.0, 275.0], [12.1, 275.0], [12.2, 275.0], [12.3, 275.0], [12.4, 275.0], [12.5, 275.0], [12.6, 276.0], [12.7, 276.0], [12.8, 276.0], [12.9, 276.0], [13.0, 276.0], [13.1, 276.0], [13.2, 276.0], [13.3, 276.0], [13.4, 276.0], [13.5, 276.0], [13.6, 276.0], [13.7, 276.0], [13.8, 276.0], [13.9, 276.0], [14.0, 277.0], [14.1, 277.0], [14.2, 277.0], [14.3, 277.0], [14.4, 277.0], [14.5, 277.0], [14.6, 277.0], [14.7, 277.0], [14.8, 277.0], [14.9, 277.0], [15.0, 277.0], [15.1, 277.0], [15.2, 277.0], [15.3, 277.0], [15.4, 278.0], [15.5, 278.0], [15.6, 278.0], [15.7, 278.0], [15.8, 278.0], [15.9, 278.0], [16.0, 278.0], [16.1, 278.0], [16.2, 278.0], [16.3, 278.0], [16.4, 278.0], [16.5, 278.0], [16.6, 278.0], [16.7, 278.0], [16.8, 278.0], [16.9, 278.0], [17.0, 278.0], [17.1, 278.0], [17.2, 278.0], [17.3, 279.0], [17.4, 279.0], [17.5, 279.0], [17.6, 279.0], [17.7, 279.0], [17.8, 279.0], [17.9, 279.0], [18.0, 279.0], [18.1, 279.0], [18.2, 279.0], [18.3, 279.0], [18.4, 279.0], [18.5, 279.0], [18.6, 280.0], [18.7, 280.0], [18.8, 280.0], [18.9, 280.0], [19.0, 280.0], [19.1, 280.0], [19.2, 280.0], [19.3, 280.0], [19.4, 280.0], [19.5, 280.0], [19.6, 280.0], [19.7, 280.0], [19.8, 280.0], [19.9, 280.0], [20.0, 280.0], [20.1, 280.0], [20.2, 281.0], [20.3, 281.0], [20.4, 281.0], [20.5, 281.0], [20.6, 281.0], [20.7, 281.0], [20.8, 281.0], [20.9, 281.0], [21.0, 281.0], [21.1, 281.0], [21.2, 281.0], [21.3, 281.0], [21.4, 281.0], [21.5, 281.0], [21.6, 281.0], [21.7, 282.0], [21.8, 282.0], [21.9, 282.0], [22.0, 282.0], [22.1, 282.0], [22.2, 282.0], [22.3, 282.0], [22.4, 282.0], [22.5, 282.0], [22.6, 282.0], [22.7, 282.0], [22.8, 282.0], [22.9, 282.0], [23.0, 282.0], [23.1, 282.0], [23.2, 282.0], [23.3, 282.0], [23.4, 283.0], [23.5, 283.0], [23.6, 283.0], [23.7, 283.0], [23.8, 283.0], [23.9, 283.0], [24.0, 283.0], [24.1, 283.0], [24.2, 283.0], [24.3, 283.0], [24.4, 283.0], [24.5, 283.0], [24.6, 284.0], [24.7, 284.0], [24.8, 284.0], [24.9, 284.0], [25.0, 284.0], [25.1, 284.0], [25.2, 284.0], [25.3, 284.0], [25.4, 284.0], [25.5, 284.0], [25.6, 284.0], [25.7, 284.0], [25.8, 284.0], [25.9, 285.0], [26.0, 285.0], [26.1, 285.0], [26.2, 285.0], [26.3, 285.0], [26.4, 285.0], [26.5, 286.0], [26.6, 286.0], [26.7, 286.0], [26.8, 286.0], [26.9, 286.0], [27.0, 287.0], [27.1, 287.0], [27.2, 287.0], [27.3, 287.0], [27.4, 288.0], [27.5, 288.0], [27.6, 288.0], [27.7, 288.0], [27.8, 288.0], [27.9, 288.0], [28.0, 288.0], [28.1, 288.0], [28.2, 288.0], [28.3, 288.0], [28.4, 288.0], [28.5, 289.0], [28.6, 289.0], [28.7, 289.0], [28.8, 289.0], [28.9, 289.0], [29.0, 289.0], [29.1, 289.0], [29.2, 289.0], [29.3, 289.0], [29.4, 289.0], [29.5, 289.0], [29.6, 289.0], [29.7, 290.0], [29.8, 290.0], [29.9, 290.0], [30.0, 290.0], [30.1, 290.0], [30.2, 290.0], [30.3, 290.0], [30.4, 290.0], [30.5, 290.0], [30.6, 290.0], [30.7, 291.0], [30.8, 291.0], [30.9, 291.0], [31.0, 291.0], [31.1, 291.0], [31.2, 291.0], [31.3, 292.0], [31.4, 292.0], [31.5, 292.0], [31.6, 292.0], [31.7, 292.0], [31.8, 292.0], [31.9, 292.0], [32.0, 292.0], [32.1, 292.0], [32.2, 292.0], [32.3, 293.0], [32.4, 293.0], [32.5, 293.0], [32.6, 293.0], [32.7, 293.0], [32.8, 293.0], [32.9, 293.0], [33.0, 293.0], [33.1, 293.0], [33.2, 293.0], [33.3, 293.0], [33.4, 293.0], [33.5, 293.0], [33.6, 293.0], [33.7, 293.0], [33.8, 294.0], [33.9, 294.0], [34.0, 294.0], [34.1, 294.0], [34.2, 294.0], [34.3, 294.0], [34.4, 294.0], [34.5, 295.0], [34.6, 295.0], [34.7, 295.0], [34.8, 295.0], [34.9, 295.0], [35.0, 295.0], [35.1, 295.0], [35.2, 295.0], [35.3, 295.0], [35.4, 295.0], [35.5, 295.0], [35.6, 295.0], [35.7, 295.0], [35.8, 297.0], [35.9, 297.0], [36.0, 298.0], [36.1, 298.0], [36.2, 298.0], [36.3, 299.0], [36.4, 299.0], [36.5, 299.0], [36.6, 299.0], [36.7, 299.0], [36.8, 299.0], [36.9, 299.0], [37.0, 300.0], [37.1, 300.0], [37.2, 300.0], [37.3, 300.0], [37.4, 300.0], [37.5, 300.0], [37.6, 301.0], [37.7, 301.0], [37.8, 301.0], [37.9, 301.0], [38.0, 301.0], [38.1, 301.0], [38.2, 301.0], [38.3, 302.0], [38.4, 302.0], [38.5, 303.0], [38.6, 303.0], [38.7, 303.0], [38.8, 303.0], [38.9, 303.0], [39.0, 304.0], [39.1, 304.0], [39.2, 304.0], [39.3, 304.0], [39.4, 304.0], [39.5, 304.0], [39.6, 305.0], [39.7, 305.0], [39.8, 305.0], [39.9, 305.0], [40.0, 306.0], [40.1, 306.0], [40.2, 306.0], [40.3, 307.0], [40.4, 307.0], [40.5, 307.0], [40.6, 308.0], [40.7, 308.0], [40.8, 309.0], [40.9, 310.0], [41.0, 310.0], [41.1, 310.0], [41.2, 310.0], [41.3, 311.0], [41.4, 311.0], [41.5, 311.0], [41.6, 311.0], [41.7, 311.0], [41.8, 311.0], [41.9, 312.0], [42.0, 312.0], [42.1, 312.0], [42.2, 312.0], [42.3, 314.0], [42.4, 317.0], [42.5, 317.0], [42.6, 317.0], [42.7, 317.0], [42.8, 317.0], [42.9, 317.0], [43.0, 317.0], [43.1, 317.0], [43.2, 317.0], [43.3, 318.0], [43.4, 318.0], [43.5, 318.0], [43.6, 318.0], [43.7, 318.0], [43.8, 318.0], [43.9, 322.0], [44.0, 322.0], [44.1, 323.0], [44.2, 323.0], [44.3, 324.0], [44.4, 326.0], [44.5, 326.0], [44.6, 326.0], [44.7, 326.0], [44.8, 326.0], [44.9, 327.0], [45.0, 327.0], [45.1, 327.0], [45.2, 327.0], [45.3, 327.0], [45.4, 328.0], [45.5, 328.0], [45.6, 328.0], [45.7, 329.0], [45.8, 329.0], [45.9, 329.0], [46.0, 329.0], [46.1, 329.0], [46.2, 329.0], [46.3, 329.0], [46.4, 329.0], [46.5, 329.0], [46.6, 330.0], [46.7, 330.0], [46.8, 330.0], [46.9, 330.0], [47.0, 330.0], [47.1, 331.0], [47.2, 331.0], [47.3, 331.0], [47.4, 332.0], [47.5, 332.0], [47.6, 332.0], [47.7, 332.0], [47.8, 332.0], [47.9, 333.0], [48.0, 333.0], [48.1, 333.0], [48.2, 333.0], [48.3, 333.0], [48.4, 334.0], [48.5, 334.0], [48.6, 335.0], [48.7, 335.0], [48.8, 335.0], [48.9, 335.0], [49.0, 335.0], [49.1, 335.0], [49.2, 336.0], [49.3, 336.0], [49.4, 336.0], [49.5, 336.0], [49.6, 336.0], [49.7, 336.0], [49.8, 336.0], [49.9, 337.0], [50.0, 337.0], [50.1, 337.0], [50.2, 337.0], [50.3, 337.0], [50.4, 337.0], [50.5, 337.0], [50.6, 337.0], [50.7, 338.0], [50.8, 338.0], [50.9, 338.0], [51.0, 338.0], [51.1, 338.0], [51.2, 338.0], [51.3, 338.0], [51.4, 338.0], [51.5, 338.0], [51.6, 338.0], [51.7, 338.0], [51.8, 338.0], [51.9, 339.0], [52.0, 339.0], [52.1, 339.0], [52.2, 339.0], [52.3, 339.0], [52.4, 339.0], [52.5, 340.0], [52.6, 340.0], [52.7, 340.0], [52.8, 340.0], [52.9, 341.0], [53.0, 341.0], [53.1, 341.0], [53.2, 341.0], [53.3, 341.0], [53.4, 341.0], [53.5, 341.0], [53.6, 341.0], [53.7, 341.0], [53.8, 341.0], [53.9, 341.0], [54.0, 342.0], [54.1, 342.0], [54.2, 342.0], [54.3, 342.0], [54.4, 342.0], [54.5, 342.0], [54.6, 342.0], [54.7, 342.0], [54.8, 342.0], [54.9, 342.0], [55.0, 342.0], [55.1, 342.0], [55.2, 342.0], [55.3, 343.0], [55.4, 343.0], [55.5, 343.0], [55.6, 343.0], [55.7, 343.0], [55.8, 343.0], [55.9, 343.0], [56.0, 343.0], [56.1, 343.0], [56.2, 344.0], [56.3, 344.0], [56.4, 344.0], [56.5, 344.0], [56.6, 344.0], [56.7, 344.0], [56.8, 344.0], [56.9, 344.0], [57.0, 344.0], [57.1, 344.0], [57.2, 344.0], [57.3, 344.0], [57.4, 344.0], [57.5, 344.0], [57.6, 344.0], [57.7, 345.0], [57.8, 345.0], [57.9, 345.0], [58.0, 345.0], [58.1, 345.0], [58.2, 345.0], [58.3, 346.0], [58.4, 346.0], [58.5, 346.0], [58.6, 346.0], [58.7, 347.0], [58.8, 347.0], [58.9, 347.0], [59.0, 347.0], [59.1, 347.0], [59.2, 347.0], [59.3, 347.0], [59.4, 347.0], [59.5, 347.0], [59.6, 347.0], [59.7, 347.0], [59.8, 348.0], [59.9, 348.0], [60.0, 348.0], [60.1, 348.0], [60.2, 348.0], [60.3, 349.0], [60.4, 349.0], [60.5, 349.0], [60.6, 349.0], [60.7, 349.0], [60.8, 349.0], [60.9, 349.0], [61.0, 349.0], [61.1, 350.0], [61.2, 350.0], [61.3, 350.0], [61.4, 350.0], [61.5, 350.0], [61.6, 351.0], [61.7, 351.0], [61.8, 351.0], [61.9, 351.0], [62.0, 351.0], [62.1, 352.0], [62.2, 352.0], [62.3, 352.0], [62.4, 352.0], [62.5, 352.0], [62.6, 352.0], [62.7, 352.0], [62.8, 352.0], [62.9, 352.0], [63.0, 352.0], [63.1, 352.0], [63.2, 352.0], [63.3, 352.0], [63.4, 352.0], [63.5, 353.0], [63.6, 353.0], [63.7, 353.0], [63.8, 353.0], [63.9, 353.0], [64.0, 353.0], [64.1, 353.0], [64.2, 353.0], [64.3, 353.0], [64.4, 353.0], [64.5, 354.0], [64.6, 354.0], [64.7, 354.0], [64.8, 354.0], [64.9, 354.0], [65.0, 354.0], [65.1, 355.0], [65.2, 355.0], [65.3, 355.0], [65.4, 355.0], [65.5, 355.0], [65.6, 355.0], [65.7, 355.0], [65.8, 355.0], [65.9, 355.0], [66.0, 355.0], [66.1, 356.0], [66.2, 356.0], [66.3, 356.0], [66.4, 356.0], [66.5, 356.0], [66.6, 356.0], [66.7, 356.0], [66.8, 356.0], [66.9, 357.0], [67.0, 357.0], [67.1, 357.0], [67.2, 357.0], [67.3, 357.0], [67.4, 357.0], [67.5, 357.0], [67.6, 358.0], [67.7, 358.0], [67.8, 358.0], [67.9, 358.0], [68.0, 358.0], [68.1, 358.0], [68.2, 358.0], [68.3, 359.0], [68.4, 359.0], [68.5, 359.0], [68.6, 359.0], [68.7, 359.0], [68.8, 359.0], [68.9, 360.0], [69.0, 360.0], [69.1, 360.0], [69.2, 360.0], [69.3, 361.0], [69.4, 361.0], [69.5, 361.0], [69.6, 361.0], [69.7, 361.0], [69.8, 361.0], [69.9, 361.0], [70.0, 361.0], [70.1, 361.0], [70.2, 361.0], [70.3, 361.0], [70.4, 362.0], [70.5, 362.0], [70.6, 362.0], [70.7, 362.0], [70.8, 362.0], [70.9, 362.0], [71.0, 362.0], [71.1, 362.0], [71.2, 363.0], [71.3, 363.0], [71.4, 363.0], [71.5, 363.0], [71.6, 363.0], [71.7, 364.0], [71.8, 364.0], [71.9, 364.0], [72.0, 364.0], [72.1, 364.0], [72.2, 364.0], [72.3, 364.0], [72.4, 364.0], [72.5, 364.0], [72.6, 364.0], [72.7, 365.0], [72.8, 365.0], [72.9, 365.0], [73.0, 365.0], [73.1, 365.0], [73.2, 365.0], [73.3, 365.0], [73.4, 365.0], [73.5, 365.0], [73.6, 366.0], [73.7, 366.0], [73.8, 366.0], [73.9, 366.0], [74.0, 366.0], [74.1, 367.0], [74.2, 367.0], [74.3, 367.0], [74.4, 367.0], [74.5, 367.0], [74.6, 367.0], [74.7, 367.0], [74.8, 367.0], [74.9, 367.0], [75.0, 367.0], [75.1, 368.0], [75.2, 368.0], [75.3, 368.0], [75.4, 368.0], [75.5, 368.0], [75.6, 368.0], [75.7, 368.0], [75.8, 368.0], [75.9, 368.0], [76.0, 369.0], [76.1, 369.0], [76.2, 369.0], [76.3, 369.0], [76.4, 369.0], [76.5, 369.0], [76.6, 369.0], [76.7, 369.0], [76.8, 369.0], [76.9, 370.0], [77.0, 370.0], [77.1, 370.0], [77.2, 371.0], [77.3, 371.0], [77.4, 371.0], [77.5, 372.0], [77.6, 372.0], [77.7, 372.0], [77.8, 372.0], [77.9, 372.0], [78.0, 372.0], [78.1, 372.0], [78.2, 373.0], [78.3, 373.0], [78.4, 374.0], [78.5, 374.0], [78.6, 374.0], [78.7, 375.0], [78.8, 375.0], [78.9, 375.0], [79.0, 375.0], [79.1, 375.0], [79.2, 376.0], [79.3, 376.0], [79.4, 376.0], [79.5, 376.0], [79.6, 376.0], [79.7, 376.0], [79.8, 376.0], [79.9, 376.0], [80.0, 377.0], [80.1, 377.0], [80.2, 378.0], [80.3, 378.0], [80.4, 378.0], [80.5, 379.0], [80.6, 379.0], [80.7, 379.0], [80.8, 379.0], [80.9, 379.0], [81.0, 380.0], [81.1, 380.0], [81.2, 382.0], [81.3, 382.0], [81.4, 382.0], [81.5, 383.0], [81.6, 383.0], [81.7, 383.0], [81.8, 384.0], [81.9, 384.0], [82.0, 384.0], [82.1, 384.0], [82.2, 386.0], [82.3, 386.0], [82.4, 386.0], [82.5, 386.0], [82.6, 386.0], [82.7, 386.0], [82.8, 387.0], [82.9, 387.0], [83.0, 387.0], [83.1, 387.0], [83.2, 388.0], [83.3, 390.0], [83.4, 390.0], [83.5, 390.0], [83.6, 390.0], [83.7, 391.0], [83.8, 391.0], [83.9, 391.0], [84.0, 391.0], [84.1, 391.0], [84.2, 392.0], [84.3, 392.0], [84.4, 392.0], [84.5, 393.0], [84.6, 393.0], [84.7, 394.0], [84.8, 395.0], [84.9, 395.0], [85.0, 395.0], [85.1, 397.0], [85.2, 397.0], [85.3, 397.0], [85.4, 397.0], [85.5, 399.0], [85.6, 399.0], [85.7, 399.0], [85.8, 400.0], [85.9, 400.0], [86.0, 401.0], [86.1, 401.0], [86.2, 401.0], [86.3, 403.0], [86.4, 403.0], [86.5, 405.0], [86.6, 405.0], [86.7, 405.0], [86.8, 413.0], [86.9, 413.0], [87.0, 414.0], [87.1, 414.0], [87.2, 414.0], [87.3, 415.0], [87.4, 415.0], [87.5, 415.0], [87.6, 418.0], [87.7, 418.0], [87.8, 422.0], [87.9, 422.0], [88.0, 424.0], [88.1, 424.0], [88.2, 424.0], [88.3, 429.0], [88.4, 429.0], [88.5, 430.0], [88.6, 432.0], [88.7, 432.0], [88.8, 437.0], [88.9, 437.0], [89.0, 446.0], [89.1, 446.0], [89.2, 446.0], [89.3, 448.0], [89.4, 448.0], [89.5, 449.0], [89.6, 452.0], [89.7, 452.0], [89.8, 452.0], [89.9, 452.0], [90.0, 453.0], [90.1, 457.0], [90.2, 457.0], [90.3, 464.0], [90.4, 466.0], [90.5, 466.0], [90.6, 467.0], [90.7, 467.0], [90.8, 469.0], [90.9, 473.0], [91.0, 473.0], [91.1, 482.0], [91.2, 482.0], [91.3, 484.0], [91.4, 486.0], [91.5, 486.0], [91.6, 486.0], [91.7, 486.0], [91.8, 486.0], [91.9, 488.0], [92.0, 488.0], [92.1, 491.0], [92.2, 491.0], [92.3, 493.0], [92.4, 493.0], [92.5, 493.0], [92.6, 494.0], [92.7, 494.0], [92.8, 496.0], [92.9, 496.0], [93.0, 496.0], [93.1, 505.0], [93.2, 505.0], [93.3, 508.0], [93.4, 511.0], [93.5, 511.0], [93.6, 512.0], [93.7, 512.0], [93.8, 529.0], [93.9, 545.0], [94.0, 545.0], [94.1, 571.0], [94.2, 571.0], [94.3, 572.0], [94.4, 573.0], [94.5, 573.0], [94.6, 573.0], [94.7, 573.0], [94.8, 581.0], [94.9, 589.0], [95.0, 589.0], [95.1, 592.0], [95.2, 603.0], [95.3, 603.0], [95.4, 605.0], [95.5, 605.0], [95.6, 609.0], [95.7, 609.0], [95.8, 609.0], [95.9, 611.0], [96.0, 611.0], [96.1, 618.0], [96.2, 623.0], [96.3, 623.0], [96.4, 623.0], [96.5, 623.0], [96.6, 624.0], [96.7, 625.0], [96.8, 625.0], [96.9, 634.0], [97.0, 634.0], [97.1, 634.0], [97.2, 636.0], [97.3, 636.0], [97.4, 637.0], [97.5, 637.0], [97.6, 639.0], [97.7, 646.0], [97.8, 646.0], [97.9, 648.0], [98.0, 648.0], [98.1, 649.0], [98.2, 661.0], [98.3, 661.0], [98.4, 664.0], [98.5, 664.0], [98.6, 689.0], [98.7, 723.0], [98.8, 723.0], [98.9, 724.0], [99.0, 724.0], [99.1, 729.0], [99.2, 738.0], [99.3, 738.0], [99.4, 748.0], [99.5, 748.0], [99.6, 752.0], [99.7, 756.0], [99.8, 756.0], [99.9, 832.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
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
        data: {"result": {"minY": 1.0, "minX": 200.0, "maxY": 295.0, "series": [{"data": [[600.0, 21.0], [300.0, 295.0], [700.0, 7.0], [400.0, 44.0], [200.0, 223.0], [800.0, 1.0], [500.0, 13.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 800.0, "title": "Response Time Distribution"}},
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
        data: {"result": {"minY": 42.0, "minX": 0.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 562.0, "series": [{"data": [[0.0, 562.0]], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [[1.0, 42.0]], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 1.0, "title": "Synthetic Response Times Distribution"}},
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
        data: {"result": {"minY": 44.18939393939392, "minX": 1.79222016E12, "maxY": 56.25423728813559, "series": [{"data": [[1.79222016E12, 44.18939393939392], [1.79222022E12, 56.25423728813559]], "isOverall": false, "label": "Virtual Users", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222022E12, "title": "Active Threads Over Time"}},
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
        data: {"result": {"minY": 278.0, "minX": 1.0, "maxY": 756.0, "series": [{"data": [[2.0, 280.0], [3.0, 311.0], [4.0, 279.0], [5.0, 330.0], [6.0, 293.0], [7.0, 327.0], [8.0, 342.0], [9.0, 513.4], [11.0, 489.0], [12.0, 443.0], [13.0, 452.16666666666663], [14.0, 756.0], [15.0, 568.5], [16.0, 391.0], [17.0, 491.2], [18.0, 475.5], [19.0, 541.3333333333334], [20.0, 467.3333333333333], [21.0, 356.5], [22.0, 293.5], [23.0, 447.0], [24.0, 394.3333333333333], [25.0, 496.75], [26.0, 388.0], [27.0, 340.5], [28.0, 480.0], [29.0, 497.0], [30.0, 365.5], [31.0, 550.75], [32.0, 469.3333333333333], [33.0, 386.0], [35.0, 461.0], [34.0, 341.0], [36.0, 371.75], [37.0, 468.75], [38.0, 334.0], [39.0, 393.5], [40.0, 531.5], [41.0, 417.5], [42.0, 337.6666666666667], [43.0, 317.0], [44.0, 281.3333333333333], [45.0, 508.0], [46.0, 505.3333333333333], [47.0, 459.0], [49.0, 381.5], [48.0, 278.0], [50.0, 427.6666666666667], [51.0, 380.5], [52.0, 403.6], [53.0, 350.0], [55.0, 453.0], [54.0, 335.0], [56.0, 451.75], [57.0, 358.0], [58.0, 395.5], [59.0, 462.5], [60.0, 325.7935483870968], [1.0, 368.0]], "isOverall": false, "label": "API Request", "isController": false}, {"data": [[53.61754966887422, 350.2235099337751]], "isOverall": false, "label": "API Request-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 60.0, "title": "Time VS Threads"}},
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
        data : {"result": {"minY": 275.0, "minX": 1.79222016E12, "maxY": 16161.833333333334, "series": [{"data": [[1.79222016E12, 4520.05], [1.79222022E12, 16161.833333333334]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.79222016E12, 275.0], [1.79222022E12, 983.3333333333334]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222022E12, "title": "Bytes Throughput Over Time"}},
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
        data: {"result": {"minY": 325.0614406779658, "minX": 1.79222016E12, "maxY": 440.19696969696975, "series": [{"data": [[1.79222016E12, 440.19696969696975], [1.79222022E12, 325.0614406779658]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222022E12, "title": "Response Time Over Time"}},
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
        data: {"result": {"minY": 324.26694915254234, "minX": 1.79222016E12, "maxY": 439.6818181818183, "series": [{"data": [[1.79222016E12, 439.6818181818183], [1.79222022E12, 324.26694915254234]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222022E12, "title": "Latencies Over Time"}},
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
        data: {"result": {"minY": 0.0, "minX": 1.79222016E12, "maxY": 112.56060606060613, "series": [{"data": [[1.79222016E12, 112.56060606060613], [1.79222022E12, 0.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222022E12, "title": "Connect Time Over Time"}},
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
        data: {"result": {"minY": 259.0, "minX": 1.79222016E12, "maxY": 832.0, "series": [{"data": [[1.79222016E12, 832.0], [1.79222022E12, 756.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.79222016E12, 261.0], [1.79222022E12, 259.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.79222016E12, 643.9], [1.79222022E12, 381.4]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.79222016E12, 805.599999999999], [1.79222022E12, 447.8899999999999]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.79222016E12, 392.5], [1.79222022E12, 325.0]], "isOverall": false, "label": "Median", "isController": false}, {"data": [[1.79222016E12, 723.35], [1.79222022E12, 399.34999999999997]], "isOverall": false, "label": "95th percentile", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222022E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
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
    data: {"result": {"minY": 281.5, "minX": 4.0, "maxY": 569.0, "series": [{"data": [[4.0, 345.5], [8.0, 357.5], [18.0, 569.0], [9.0, 330.0], [19.0, 466.5], [20.0, 489.5], [5.0, 281.5], [10.0, 304.5], [11.0, 338.0], [6.0, 345.0], [7.0, 311.0], [15.0, 511.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 20.0, "title": "Response Time Vs Request"}},
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
    data: {"result": {"minY": 281.0, "minX": 4.0, "maxY": 569.0, "series": [{"data": [[4.0, 343.5], [8.0, 357.5], [18.0, 569.0], [9.0, 329.0], [19.0, 466.0], [20.0, 489.0], [5.0, 281.0], [10.0, 304.0], [11.0, 335.0], [6.0, 345.0], [7.0, 311.0], [15.0, 511.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 20.0, "title": "Latencies Vs Request"}},
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
        data: {"result": {"minY": 2.25, "minX": 1.79222016E12, "maxY": 7.816666666666666, "series": [{"data": [[1.79222016E12, 2.25], [1.79222022E12, 7.816666666666666]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222022E12, "title": "Hits Per Second"}},
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
        data: {"result": {"minY": 2.2, "minX": 1.79222016E12, "maxY": 7.866666666666666, "series": [{"data": [[1.79222016E12, 2.2], [1.79222022E12, 7.866666666666666]], "isOverall": false, "label": "200", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222022E12, "title": "Codes Per Second"}},
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
        data: {"result": {"minY": 2.2, "minX": 1.79222016E12, "maxY": 7.866666666666666, "series": [{"data": [[1.79222016E12, 2.2], [1.79222022E12, 7.866666666666666]], "isOverall": false, "label": "API Request-success", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222022E12, "title": "Transactions Per Second"}},
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
        data: {"result": {"minY": 2.2, "minX": 1.79222016E12, "maxY": 7.866666666666666, "series": [{"data": [[1.79222016E12, 2.2], [1.79222022E12, 7.866666666666666]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222022E12, "title": "Total Transactions Per Second"}},
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

