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
        data: {"result": {"minY": 80.0, "minX": 0.0, "maxY": 3784.0, "series": [{"data": [[0.0, 80.0], [0.1, 80.0], [0.2, 252.0], [0.3, 255.0], [0.4, 256.0], [0.5, 256.0], [0.6, 257.0], [0.7, 257.0], [0.8, 257.0], [0.9, 258.0], [1.0, 259.0], [1.1, 259.0], [1.2, 259.0], [1.3, 260.0], [1.4, 260.0], [1.5, 260.0], [1.6, 260.0], [1.7, 261.0], [1.8, 261.0], [1.9, 261.0], [2.0, 261.0], [2.1, 261.0], [2.2, 261.0], [2.3, 261.0], [2.4, 262.0], [2.5, 262.0], [2.6, 262.0], [2.7, 262.0], [2.8, 262.0], [2.9, 262.0], [3.0, 263.0], [3.1, 263.0], [3.2, 263.0], [3.3, 263.0], [3.4, 263.0], [3.5, 264.0], [3.6, 264.0], [3.7, 264.0], [3.8, 264.0], [3.9, 264.0], [4.0, 264.0], [4.1, 264.0], [4.2, 264.0], [4.3, 265.0], [4.4, 265.0], [4.5, 265.0], [4.6, 265.0], [4.7, 265.0], [4.8, 266.0], [4.9, 266.0], [5.0, 266.0], [5.1, 266.0], [5.2, 266.0], [5.3, 266.0], [5.4, 266.0], [5.5, 266.0], [5.6, 266.0], [5.7, 267.0], [5.8, 267.0], [5.9, 267.0], [6.0, 267.0], [6.1, 267.0], [6.2, 267.0], [6.3, 267.0], [6.4, 267.0], [6.5, 268.0], [6.6, 268.0], [6.7, 268.0], [6.8, 268.0], [6.9, 268.0], [7.0, 268.0], [7.1, 268.0], [7.2, 268.0], [7.3, 269.0], [7.4, 269.0], [7.5, 269.0], [7.6, 269.0], [7.7, 269.0], [7.8, 269.0], [7.9, 269.0], [8.0, 269.0], [8.1, 269.0], [8.2, 269.0], [8.3, 269.0], [8.4, 269.0], [8.5, 269.0], [8.6, 269.0], [8.7, 269.0], [8.8, 270.0], [8.9, 270.0], [9.0, 270.0], [9.1, 270.0], [9.2, 270.0], [9.3, 270.0], [9.4, 270.0], [9.5, 270.0], [9.6, 270.0], [9.7, 270.0], [9.8, 271.0], [9.9, 271.0], [10.0, 271.0], [10.1, 271.0], [10.2, 271.0], [10.3, 271.0], [10.4, 271.0], [10.5, 271.0], [10.6, 271.0], [10.7, 271.0], [10.8, 271.0], [10.9, 271.0], [11.0, 271.0], [11.1, 271.0], [11.2, 271.0], [11.3, 271.0], [11.4, 271.0], [11.5, 271.0], [11.6, 272.0], [11.7, 272.0], [11.8, 272.0], [11.9, 272.0], [12.0, 272.0], [12.1, 272.0], [12.2, 272.0], [12.3, 272.0], [12.4, 273.0], [12.5, 273.0], [12.6, 273.0], [12.7, 273.0], [12.8, 273.0], [12.9, 273.0], [13.0, 273.0], [13.1, 273.0], [13.2, 273.0], [13.3, 273.0], [13.4, 273.0], [13.5, 273.0], [13.6, 273.0], [13.7, 273.0], [13.8, 273.0], [13.9, 274.0], [14.0, 274.0], [14.1, 274.0], [14.2, 274.0], [14.3, 274.0], [14.4, 274.0], [14.5, 274.0], [14.6, 274.0], [14.7, 274.0], [14.8, 274.0], [14.9, 274.0], [15.0, 274.0], [15.1, 274.0], [15.2, 274.0], [15.3, 274.0], [15.4, 274.0], [15.5, 274.0], [15.6, 275.0], [15.7, 275.0], [15.8, 275.0], [15.9, 275.0], [16.0, 275.0], [16.1, 275.0], [16.2, 275.0], [16.3, 275.0], [16.4, 275.0], [16.5, 275.0], [16.6, 275.0], [16.7, 275.0], [16.8, 276.0], [16.9, 276.0], [17.0, 276.0], [17.1, 276.0], [17.2, 276.0], [17.3, 276.0], [17.4, 276.0], [17.5, 276.0], [17.6, 276.0], [17.7, 276.0], [17.8, 276.0], [17.9, 276.0], [18.0, 276.0], [18.1, 276.0], [18.2, 276.0], [18.3, 276.0], [18.4, 277.0], [18.5, 277.0], [18.6, 277.0], [18.7, 277.0], [18.8, 277.0], [18.9, 277.0], [19.0, 277.0], [19.1, 277.0], [19.2, 277.0], [19.3, 277.0], [19.4, 277.0], [19.5, 277.0], [19.6, 277.0], [19.7, 277.0], [19.8, 277.0], [19.9, 277.0], [20.0, 278.0], [20.1, 278.0], [20.2, 278.0], [20.3, 278.0], [20.4, 278.0], [20.5, 278.0], [20.6, 278.0], [20.7, 278.0], [20.8, 278.0], [20.9, 278.0], [21.0, 279.0], [21.1, 279.0], [21.2, 279.0], [21.3, 279.0], [21.4, 279.0], [21.5, 279.0], [21.6, 279.0], [21.7, 279.0], [21.8, 279.0], [21.9, 279.0], [22.0, 279.0], [22.1, 279.0], [22.2, 279.0], [22.3, 279.0], [22.4, 279.0], [22.5, 279.0], [22.6, 280.0], [22.7, 280.0], [22.8, 280.0], [22.9, 280.0], [23.0, 280.0], [23.1, 280.0], [23.2, 280.0], [23.3, 280.0], [23.4, 281.0], [23.5, 281.0], [23.6, 281.0], [23.7, 281.0], [23.8, 281.0], [23.9, 281.0], [24.0, 281.0], [24.1, 281.0], [24.2, 281.0], [24.3, 281.0], [24.4, 281.0], [24.5, 281.0], [24.6, 281.0], [24.7, 281.0], [24.8, 281.0], [24.9, 282.0], [25.0, 282.0], [25.1, 282.0], [25.2, 282.0], [25.3, 282.0], [25.4, 282.0], [25.5, 282.0], [25.6, 282.0], [25.7, 282.0], [25.8, 282.0], [25.9, 282.0], [26.0, 282.0], [26.1, 282.0], [26.2, 282.0], [26.3, 282.0], [26.4, 282.0], [26.5, 282.0], [26.6, 282.0], [26.7, 283.0], [26.8, 283.0], [26.9, 283.0], [27.0, 283.0], [27.1, 283.0], [27.2, 283.0], [27.3, 283.0], [27.4, 283.0], [27.5, 283.0], [27.6, 284.0], [27.7, 284.0], [27.8, 284.0], [27.9, 284.0], [28.0, 284.0], [28.1, 284.0], [28.2, 284.0], [28.3, 284.0], [28.4, 284.0], [28.5, 284.0], [28.6, 284.0], [28.7, 285.0], [28.8, 285.0], [28.9, 285.0], [29.0, 285.0], [29.1, 285.0], [29.2, 285.0], [29.3, 285.0], [29.4, 285.0], [29.5, 285.0], [29.6, 286.0], [29.7, 286.0], [29.8, 286.0], [29.9, 286.0], [30.0, 286.0], [30.1, 286.0], [30.2, 286.0], [30.3, 286.0], [30.4, 286.0], [30.5, 286.0], [30.6, 286.0], [30.7, 286.0], [30.8, 286.0], [30.9, 286.0], [31.0, 286.0], [31.1, 287.0], [31.2, 287.0], [31.3, 287.0], [31.4, 287.0], [31.5, 287.0], [31.6, 287.0], [31.7, 287.0], [31.8, 287.0], [31.9, 287.0], [32.0, 288.0], [32.1, 288.0], [32.2, 288.0], [32.3, 288.0], [32.4, 288.0], [32.5, 288.0], [32.6, 288.0], [32.7, 288.0], [32.8, 288.0], [32.9, 288.0], [33.0, 289.0], [33.1, 289.0], [33.2, 289.0], [33.3, 289.0], [33.4, 289.0], [33.5, 289.0], [33.6, 289.0], [33.7, 289.0], [33.8, 290.0], [33.9, 290.0], [34.0, 290.0], [34.1, 290.0], [34.2, 290.0], [34.3, 290.0], [34.4, 290.0], [34.5, 290.0], [34.6, 290.0], [34.7, 290.0], [34.8, 291.0], [34.9, 291.0], [35.0, 291.0], [35.1, 291.0], [35.2, 291.0], [35.3, 291.0], [35.4, 292.0], [35.5, 292.0], [35.6, 292.0], [35.7, 292.0], [35.8, 292.0], [35.9, 292.0], [36.0, 292.0], [36.1, 292.0], [36.2, 292.0], [36.3, 292.0], [36.4, 292.0], [36.5, 292.0], [36.6, 292.0], [36.7, 292.0], [36.8, 293.0], [36.9, 293.0], [37.0, 293.0], [37.1, 293.0], [37.2, 293.0], [37.3, 293.0], [37.4, 293.0], [37.5, 293.0], [37.6, 293.0], [37.7, 293.0], [37.8, 293.0], [37.9, 293.0], [38.0, 294.0], [38.1, 294.0], [38.2, 294.0], [38.3, 294.0], [38.4, 294.0], [38.5, 294.0], [38.6, 294.0], [38.7, 294.0], [38.8, 294.0], [38.9, 294.0], [39.0, 295.0], [39.1, 295.0], [39.2, 295.0], [39.3, 295.0], [39.4, 295.0], [39.5, 295.0], [39.6, 295.0], [39.7, 295.0], [39.8, 295.0], [39.9, 295.0], [40.0, 295.0], [40.1, 295.0], [40.2, 295.0], [40.3, 295.0], [40.4, 295.0], [40.5, 295.0], [40.6, 296.0], [40.7, 296.0], [40.8, 296.0], [40.9, 296.0], [41.0, 296.0], [41.1, 296.0], [41.2, 296.0], [41.3, 296.0], [41.4, 296.0], [41.5, 297.0], [41.6, 297.0], [41.7, 297.0], [41.8, 297.0], [41.9, 297.0], [42.0, 297.0], [42.1, 297.0], [42.2, 297.0], [42.3, 298.0], [42.4, 298.0], [42.5, 298.0], [42.6, 298.0], [42.7, 298.0], [42.8, 298.0], [42.9, 298.0], [43.0, 298.0], [43.1, 298.0], [43.2, 299.0], [43.3, 300.0], [43.4, 300.0], [43.5, 300.0], [43.6, 300.0], [43.7, 300.0], [43.8, 300.0], [43.9, 300.0], [44.0, 300.0], [44.1, 300.0], [44.2, 300.0], [44.3, 301.0], [44.4, 301.0], [44.5, 301.0], [44.6, 301.0], [44.7, 301.0], [44.8, 301.0], [44.9, 301.0], [45.0, 301.0], [45.1, 301.0], [45.2, 301.0], [45.3, 301.0], [45.4, 302.0], [45.5, 302.0], [45.6, 302.0], [45.7, 302.0], [45.8, 302.0], [45.9, 302.0], [46.0, 302.0], [46.1, 302.0], [46.2, 303.0], [46.3, 303.0], [46.4, 303.0], [46.5, 303.0], [46.6, 303.0], [46.7, 303.0], [46.8, 303.0], [46.9, 303.0], [47.0, 303.0], [47.1, 303.0], [47.2, 303.0], [47.3, 304.0], [47.4, 304.0], [47.5, 304.0], [47.6, 304.0], [47.7, 304.0], [47.8, 304.0], [47.9, 304.0], [48.0, 304.0], [48.1, 304.0], [48.2, 304.0], [48.3, 305.0], [48.4, 305.0], [48.5, 305.0], [48.6, 305.0], [48.7, 305.0], [48.8, 305.0], [48.9, 305.0], [49.0, 305.0], [49.1, 305.0], [49.2, 305.0], [49.3, 305.0], [49.4, 305.0], [49.5, 306.0], [49.6, 306.0], [49.7, 306.0], [49.8, 306.0], [49.9, 306.0], [50.0, 306.0], [50.1, 306.0], [50.2, 306.0], [50.3, 306.0], [50.4, 306.0], [50.5, 307.0], [50.6, 307.0], [50.7, 307.0], [50.8, 308.0], [50.9, 308.0], [51.0, 308.0], [51.1, 308.0], [51.2, 308.0], [51.3, 309.0], [51.4, 309.0], [51.5, 309.0], [51.6, 310.0], [51.7, 310.0], [51.8, 310.0], [51.9, 310.0], [52.0, 310.0], [52.1, 310.0], [52.2, 310.0], [52.3, 310.0], [52.4, 310.0], [52.5, 310.0], [52.6, 310.0], [52.7, 311.0], [52.8, 311.0], [52.9, 311.0], [53.0, 311.0], [53.1, 311.0], [53.2, 311.0], [53.3, 312.0], [53.4, 312.0], [53.5, 312.0], [53.6, 313.0], [53.7, 313.0], [53.8, 313.0], [53.9, 313.0], [54.0, 313.0], [54.1, 314.0], [54.2, 314.0], [54.3, 315.0], [54.4, 315.0], [54.5, 316.0], [54.6, 316.0], [54.7, 316.0], [54.8, 316.0], [54.9, 316.0], [55.0, 316.0], [55.1, 317.0], [55.2, 317.0], [55.3, 317.0], [55.4, 318.0], [55.5, 319.0], [55.6, 319.0], [55.7, 319.0], [55.8, 319.0], [55.9, 319.0], [56.0, 319.0], [56.1, 320.0], [56.2, 320.0], [56.3, 321.0], [56.4, 321.0], [56.5, 321.0], [56.6, 321.0], [56.7, 322.0], [56.8, 322.0], [56.9, 322.0], [57.0, 322.0], [57.1, 322.0], [57.2, 323.0], [57.3, 323.0], [57.4, 323.0], [57.5, 323.0], [57.6, 323.0], [57.7, 324.0], [57.8, 324.0], [57.9, 324.0], [58.0, 324.0], [58.1, 324.0], [58.2, 325.0], [58.3, 325.0], [58.4, 325.0], [58.5, 326.0], [58.6, 327.0], [58.7, 327.0], [58.8, 328.0], [58.9, 329.0], [59.0, 329.0], [59.1, 329.0], [59.2, 329.0], [59.3, 329.0], [59.4, 331.0], [59.5, 331.0], [59.6, 331.0], [59.7, 332.0], [59.8, 332.0], [59.9, 333.0], [60.0, 333.0], [60.1, 334.0], [60.2, 335.0], [60.3, 335.0], [60.4, 336.0], [60.5, 336.0], [60.6, 338.0], [60.7, 338.0], [60.8, 339.0], [60.9, 340.0], [61.0, 340.0], [61.1, 340.0], [61.2, 340.0], [61.3, 340.0], [61.4, 341.0], [61.5, 341.0], [61.6, 341.0], [61.7, 342.0], [61.8, 343.0], [61.9, 343.0], [62.0, 343.0], [62.1, 343.0], [62.2, 345.0], [62.3, 345.0], [62.4, 346.0], [62.5, 347.0], [62.6, 347.0], [62.7, 348.0], [62.8, 348.0], [62.9, 349.0], [63.0, 349.0], [63.1, 351.0], [63.2, 351.0], [63.3, 351.0], [63.4, 351.0], [63.5, 351.0], [63.6, 352.0], [63.7, 352.0], [63.8, 354.0], [63.9, 355.0], [64.0, 355.0], [64.1, 355.0], [64.2, 355.0], [64.3, 355.0], [64.4, 356.0], [64.5, 358.0], [64.6, 359.0], [64.7, 359.0], [64.8, 360.0], [64.9, 362.0], [65.0, 362.0], [65.1, 364.0], [65.2, 364.0], [65.3, 366.0], [65.4, 366.0], [65.5, 367.0], [65.6, 368.0], [65.7, 368.0], [65.8, 369.0], [65.9, 369.0], [66.0, 369.0], [66.1, 370.0], [66.2, 372.0], [66.3, 372.0], [66.4, 372.0], [66.5, 373.0], [66.6, 374.0], [66.7, 374.0], [66.8, 375.0], [66.9, 375.0], [67.0, 375.0], [67.1, 379.0], [67.2, 380.0], [67.3, 381.0], [67.4, 381.0], [67.5, 381.0], [67.6, 382.0], [67.7, 382.0], [67.8, 382.0], [67.9, 383.0], [68.0, 383.0], [68.1, 383.0], [68.2, 384.0], [68.3, 385.0], [68.4, 388.0], [68.5, 388.0], [68.6, 389.0], [68.7, 389.0], [68.8, 391.0], [68.9, 391.0], [69.0, 391.0], [69.1, 391.0], [69.2, 395.0], [69.3, 398.0], [69.4, 402.0], [69.5, 403.0], [69.6, 415.0], [69.7, 416.0], [69.8, 422.0], [69.9, 426.0], [70.0, 426.0], [70.1, 427.0], [70.2, 428.0], [70.3, 429.0], [70.4, 431.0], [70.5, 433.0], [70.6, 433.0], [70.7, 433.0], [70.8, 433.0], [70.9, 435.0], [71.0, 435.0], [71.1, 435.0], [71.2, 435.0], [71.3, 436.0], [71.4, 437.0], [71.5, 437.0], [71.6, 439.0], [71.7, 440.0], [71.8, 440.0], [71.9, 441.0], [72.0, 441.0], [72.1, 441.0], [72.2, 444.0], [72.3, 445.0], [72.4, 445.0], [72.5, 446.0], [72.6, 447.0], [72.7, 448.0], [72.8, 448.0], [72.9, 449.0], [73.0, 449.0], [73.1, 449.0], [73.2, 450.0], [73.3, 450.0], [73.4, 450.0], [73.5, 451.0], [73.6, 451.0], [73.7, 452.0], [73.8, 453.0], [73.9, 453.0], [74.0, 453.0], [74.1, 453.0], [74.2, 454.0], [74.3, 455.0], [74.4, 455.0], [74.5, 455.0], [74.6, 457.0], [74.7, 457.0], [74.8, 457.0], [74.9, 457.0], [75.0, 457.0], [75.1, 457.0], [75.2, 458.0], [75.3, 458.0], [75.4, 459.0], [75.5, 459.0], [75.6, 460.0], [75.7, 460.0], [75.8, 460.0], [75.9, 461.0], [76.0, 461.0], [76.1, 462.0], [76.2, 462.0], [76.3, 462.0], [76.4, 462.0], [76.5, 463.0], [76.6, 463.0], [76.7, 463.0], [76.8, 463.0], [76.9, 464.0], [77.0, 464.0], [77.1, 464.0], [77.2, 465.0], [77.3, 465.0], [77.4, 466.0], [77.5, 466.0], [77.6, 466.0], [77.7, 467.0], [77.8, 467.0], [77.9, 468.0], [78.0, 468.0], [78.1, 468.0], [78.2, 468.0], [78.3, 469.0], [78.4, 469.0], [78.5, 469.0], [78.6, 469.0], [78.7, 469.0], [78.8, 470.0], [78.9, 470.0], [79.0, 470.0], [79.1, 471.0], [79.2, 473.0], [79.3, 473.0], [79.4, 473.0], [79.5, 473.0], [79.6, 474.0], [79.7, 474.0], [79.8, 475.0], [79.9, 475.0], [80.0, 475.0], [80.1, 475.0], [80.2, 475.0], [80.3, 476.0], [80.4, 476.0], [80.5, 477.0], [80.6, 477.0], [80.7, 477.0], [80.8, 477.0], [80.9, 477.0], [81.0, 477.0], [81.1, 477.0], [81.2, 478.0], [81.3, 479.0], [81.4, 480.0], [81.5, 481.0], [81.6, 482.0], [81.7, 482.0], [81.8, 483.0], [81.9, 483.0], [82.0, 483.0], [82.1, 483.0], [82.2, 483.0], [82.3, 483.0], [82.4, 484.0], [82.5, 485.0], [82.6, 485.0], [82.7, 486.0], [82.8, 486.0], [82.9, 486.0], [83.0, 486.0], [83.1, 486.0], [83.2, 487.0], [83.3, 487.0], [83.4, 488.0], [83.5, 489.0], [83.6, 489.0], [83.7, 489.0], [83.8, 490.0], [83.9, 491.0], [84.0, 491.0], [84.1, 491.0], [84.2, 491.0], [84.3, 491.0], [84.4, 491.0], [84.5, 491.0], [84.6, 492.0], [84.7, 492.0], [84.8, 492.0], [84.9, 492.0], [85.0, 492.0], [85.1, 493.0], [85.2, 493.0], [85.3, 494.0], [85.4, 494.0], [85.5, 495.0], [85.6, 495.0], [85.7, 496.0], [85.8, 496.0], [85.9, 496.0], [86.0, 496.0], [86.1, 497.0], [86.2, 498.0], [86.3, 499.0], [86.4, 499.0], [86.5, 499.0], [86.6, 500.0], [86.7, 500.0], [86.8, 500.0], [86.9, 500.0], [87.0, 500.0], [87.1, 501.0], [87.2, 503.0], [87.3, 503.0], [87.4, 503.0], [87.5, 504.0], [87.6, 507.0], [87.7, 507.0], [87.8, 508.0], [87.9, 509.0], [88.0, 509.0], [88.1, 510.0], [88.2, 511.0], [88.3, 511.0], [88.4, 512.0], [88.5, 512.0], [88.6, 512.0], [88.7, 512.0], [88.8, 513.0], [88.9, 514.0], [89.0, 514.0], [89.1, 515.0], [89.2, 515.0], [89.3, 516.0], [89.4, 516.0], [89.5, 516.0], [89.6, 516.0], [89.7, 516.0], [89.8, 517.0], [89.9, 517.0], [90.0, 517.0], [90.1, 518.0], [90.2, 521.0], [90.3, 523.0], [90.4, 523.0], [90.5, 525.0], [90.6, 525.0], [90.7, 526.0], [90.8, 527.0], [90.9, 527.0], [91.0, 527.0], [91.1, 527.0], [91.2, 529.0], [91.3, 530.0], [91.4, 531.0], [91.5, 532.0], [91.6, 532.0], [91.7, 535.0], [91.8, 537.0], [91.9, 537.0], [92.0, 537.0], [92.1, 538.0], [92.2, 542.0], [92.3, 542.0], [92.4, 548.0], [92.5, 551.0], [92.6, 551.0], [92.7, 551.0], [92.8, 552.0], [92.9, 554.0], [93.0, 554.0], [93.1, 557.0], [93.2, 558.0], [93.3, 564.0], [93.4, 566.0], [93.5, 567.0], [93.6, 567.0], [93.7, 574.0], [93.8, 575.0], [93.9, 576.0], [94.0, 576.0], [94.1, 578.0], [94.2, 578.0], [94.3, 579.0], [94.4, 584.0], [94.5, 587.0], [94.6, 587.0], [94.7, 592.0], [94.8, 592.0], [94.9, 594.0], [95.0, 594.0], [95.1, 594.0], [95.2, 604.0], [95.3, 606.0], [95.4, 608.0], [95.5, 610.0], [95.6, 613.0], [95.7, 614.0], [95.8, 614.0], [95.9, 618.0], [96.0, 618.0], [96.1, 633.0], [96.2, 642.0], [96.3, 646.0], [96.4, 649.0], [96.5, 663.0], [96.6, 668.0], [96.7, 689.0], [96.8, 698.0], [96.9, 703.0], [97.0, 703.0], [97.1, 708.0], [97.2, 711.0], [97.3, 713.0], [97.4, 714.0], [97.5, 715.0], [97.6, 730.0], [97.7, 732.0], [97.8, 743.0], [97.9, 759.0], [98.0, 759.0], [98.1, 779.0], [98.2, 795.0], [98.3, 803.0], [98.4, 810.0], [98.5, 823.0], [98.6, 840.0], [98.7, 975.0], [98.8, 997.0], [98.9, 1000.0], [99.0, 1000.0], [99.1, 1188.0], [99.2, 1188.0], [99.3, 1890.0], [99.4, 1925.0], [99.5, 1939.0], [99.6, 1974.0], [99.7, 2051.0], [99.8, 3303.0], [99.9, 3784.0], [100.0, 3784.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
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
        data: {"result": {"minY": 1.0, "minX": 0.0, "maxY": 388.0, "series": [{"data": [[0.0, 1.0], [600.0, 16.0], [700.0, 12.0], [800.0, 4.0], [200.0, 388.0], [3300.0, 1.0], [900.0, 2.0], [3700.0, 1.0], [1000.0, 1.0], [1100.0, 2.0], [300.0, 235.0], [400.0, 155.0], [1800.0, 1.0], [1900.0, 3.0], [500.0, 77.0], [2000.0, 1.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 3700.0, "title": "Response Time Distribution"}},
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
        data: {"result": {"minY": 3.0, "minX": 0.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 780.0, "series": [{"data": [[0.0, 780.0]], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [[1.0, 110.0]], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [[2.0, 7.0]], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [[3.0, 3.0]], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 3.0, "title": "Synthetic Response Times Distribution"}},
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
        data: {"result": {"minY": 171.8421052631578, "minX": 1.79222076E12, "maxY": 194.23118279569889, "series": [{"data": [[1.79222082E12, 194.23118279569889], [1.79222076E12, 171.8421052631578]], "isOverall": false, "label": "Virtual Users", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222082E12, "title": "Active Threads Over Time"}},
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
        data: {"result": {"minY": 256.0, "minX": 3.0, "maxY": 1203.5, "series": [{"data": [[3.0, 713.0], [4.0, 367.0], [5.0, 306.0], [6.0, 272.0], [7.0, 269.0], [8.0, 278.0], [9.0, 359.0], [10.0, 286.0], [11.0, 366.0], [12.0, 358.0], [13.0, 276.0], [14.0, 275.0], [15.0, 306.0], [16.0, 273.0], [17.0, 290.0], [18.0, 269.0], [19.0, 360.0], [20.0, 304.0], [21.0, 301.0], [22.0, 294.0], [23.0, 310.0], [24.0, 306.0], [25.0, 381.0], [26.0, 295.0], [27.0, 310.0], [28.0, 273.0], [29.0, 300.0], [30.0, 263.0], [31.0, 272.0], [33.0, 301.0], [32.0, 269.0], [35.0, 554.625], [34.0, 323.0], [37.0, 485.5], [36.0, 286.0], [38.0, 443.0], [39.0, 437.0], [40.0, 590.3333333333334], [41.0, 283.0], [42.0, 381.0], [43.0, 336.0], [45.0, 447.5], [44.0, 292.0], [46.0, 393.0], [47.0, 450.5], [48.0, 402.5], [49.0, 448.0], [50.0, 542.5], [51.0, 410.0], [52.0, 420.0], [53.0, 415.5], [54.0, 393.5], [55.0, 284.0], [56.0, 390.0], [57.0, 479.0], [58.0, 546.0], [59.0, 306.0], [61.0, 473.25], [60.0, 269.0], [63.0, 452.25], [62.0, 265.0], [66.0, 382.0], [67.0, 275.0], [65.0, 285.0], [64.0, 273.0], [68.0, 385.5], [69.0, 514.0], [71.0, 280.0], [70.0, 276.0], [72.0, 465.6666666666667], [73.0, 428.6666666666667], [75.0, 272.0], [74.0, 260.0], [77.0, 454.0], [78.0, 460.75], [79.0, 289.0], [76.0, 305.0], [80.0, 406.0], [82.0, 455.3333333333333], [83.0, 426.0], [81.0, 276.0], [85.0, 417.5], [86.0, 439.3333333333333], [84.0, 347.0], [88.0, 400.75], [89.0, 527.0], [91.0, 372.0], [90.0, 321.0], [92.0, 492.3333333333333], [93.0, 375.6666666666667], [94.0, 475.0], [95.0, 323.0], [96.0, 539.6], [97.0, 385.0], [99.0, 419.3333333333333], [98.0, 267.0], [101.0, 396.5], [102.0, 324.5], [103.0, 424.0], [100.0, 287.0], [105.0, 482.5], [106.0, 384.0], [107.0, 307.0], [104.0, 281.0], [109.0, 376.5], [110.0, 387.3333333333333], [111.0, 426.0], [108.0, 283.0], [113.0, 267.0], [114.0, 293.0], [115.0, 279.0], [112.0, 264.0], [117.0, 391.0], [118.0, 387.0], [119.0, 530.3333333333334], [116.0, 338.0], [120.0, 426.0], [121.0, 312.5], [122.0, 414.75], [123.0, 434.0], [124.0, 520.0], [126.0, 418.0], [127.0, 287.0], [125.0, 305.0], [128.0, 366.0], [129.0, 380.5], [130.0, 432.5], [131.0, 432.6666666666667], [132.0, 486.0], [134.0, 375.5], [135.0, 382.5], [133.0, 375.0], [136.0, 370.5], [137.0, 433.3333333333333], [138.0, 390.5], [140.0, 419.5], [142.0, 437.75], [143.0, 415.0], [141.0, 282.0], [139.0, 289.0], [144.0, 691.8], [145.0, 504.0], [147.0, 442.75], [149.0, 377.5], [151.0, 371.8], [150.0, 258.0], [148.0, 274.0], [146.0, 341.0], [153.0, 382.0], [154.0, 404.25], [156.0, 461.5], [157.0, 403.3333333333333], [158.0, 688.6666666666666], [159.0, 266.0], [155.0, 287.0], [152.0, 279.0], [161.0, 374.5], [162.0, 390.0], [163.0, 399.0], [164.0, 286.5], [165.0, 513.6666666666666], [166.0, 440.25], [167.0, 294.0], [160.0, 293.0], [168.0, 346.0], [169.0, 497.5], [172.0, 367.0], [174.0, 440.6666666666667], [175.0, 467.5], [173.0, 261.0], [171.0, 303.0], [170.0, 278.0], [176.0, 448.0], [177.0, 468.5], [178.0, 401.0], [179.0, 373.0], [181.0, 1203.5], [182.0, 424.3333333333333], [183.0, 297.0], [180.0, 271.0], [184.0, 384.0], [185.0, 398.0], [186.0, 364.0], [188.0, 419.0], [189.0, 1150.5], [191.0, 457.0], [190.0, 276.0], [187.0, 368.0], [194.0, 278.5], [195.0, 388.0], [197.0, 903.3333333333333], [199.0, 368.25], [198.0, 440.0], [196.0, 279.0], [193.0, 274.0], [192.0, 264.0], [200.0, 470.0], [201.0, 434.3333333333333], [202.0, 376.0], [204.0, 407.6666666666667], [205.0, 289.0], [206.0, 283.0], [207.0, 546.0], [203.0, 276.0], [209.0, 374.0], [210.0, 382.0], [212.0, 548.0], [213.0, 384.0], [214.0, 373.5], [215.0, 286.0], [211.0, 355.0], [208.0, 306.0], [217.0, 377.5], [218.0, 282.5], [219.0, 414.0], [220.0, 538.0], [222.0, 376.5], [223.0, 295.0], [221.0, 301.0], [216.0, 291.0], [224.0, 499.3333333333333], [225.0, 393.3333333333333], [226.0, 266.5], [227.0, 428.6666666666667], [228.0, 406.0], [229.0, 523.0], [230.0, 491.0], [231.0, 422.0], [232.0, 546.3333333333334], [234.0, 411.0], [235.0, 416.0], [236.0, 576.5], [237.0, 371.5], [238.0, 361.0], [239.0, 352.0], [233.0, 256.0], [240.0, 380.5], [241.0, 339.3333333333333], [242.0, 363.0], [244.0, 375.0], [245.0, 410.0], [246.0, 467.6666666666667], [247.0, 293.0], [243.0, 257.0], [248.0, 285.5], [249.0, 362.0], [250.0, 337.33582089552243]], "isOverall": false, "label": "API Request", "isController": false}, {"data": [[185.72333333333333, 381.88222222222197]], "isOverall": false, "label": "API Request-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 250.0, "title": "Time VS Threads"}},
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
        data : {"result": {"minY": 729.6, "minX": 1.79222076E12, "maxY": 11058.183333333332, "series": [{"data": [[1.79222082E12, 11058.183333333332], [1.79222076E12, 6718.0]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.79222082E12, 1184.0], [1.79222076E12, 729.6]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222082E12, "title": "Bytes Throughput Over Time"}},
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
        data: {"result": {"minY": 311.5286738351252, "minX": 1.79222076E12, "maxY": 496.6695906432753, "series": [{"data": [[1.79222082E12, 311.5286738351252], [1.79222076E12, 496.6695906432753]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222082E12, "title": "Response Time Over Time"}},
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
        data: {"result": {"minY": 310.11469534050167, "minX": 1.79222076E12, "maxY": 496.63157894736844, "series": [{"data": [[1.79222082E12, 310.11469534050167], [1.79222076E12, 496.63157894736844]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222082E12, "title": "Latencies Over Time"}},
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
        data: {"result": {"minY": 0.9784946236559139, "minX": 1.79222076E12, "maxY": 180.27777777777774, "series": [{"data": [[1.79222082E12, 0.9784946236559139], [1.79222076E12, 180.27777777777774]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222082E12, "title": "Connect Time Over Time"}},
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
        data: {"result": {"minY": 252.0, "minX": 1.79222076E12, "maxY": 3784.0, "series": [{"data": [[1.79222082E12, 1925.0], [1.79222076E12, 3784.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.79222082E12, 252.0], [1.79222076E12, 256.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.79222082E12, 368.0], [1.79222076E12, 613.7]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.79222082E12, 644.7599999999953], [1.79222076E12, 2017.8899999999994]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.79222082E12, 292.0], [1.79222076E12, 475.0]], "isOverall": false, "label": "Median", "isController": false}, {"data": [[1.79222082E12, 391.0], [1.79222076E12, 731.6999999999999]], "isOverall": false, "label": "95th percentile", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222082E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
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
    data: {"result": {"minY": 80.0, "minX": 6.0, "maxY": 575.0, "series": [{"data": [[8.0, 298.0], [9.0, 295.5], [10.0, 296.0], [42.0, 461.0], [11.0, 575.0], [12.0, 288.5], [50.0, 517.0], [13.0, 292.0], [57.0, 477.0], [14.0, 289.5], [15.0, 288.0], [63.0, 474.0], [16.0, 295.0], [6.0, 282.0], [7.0, 300.0]], "isOverall": false, "label": "Successes", "isController": false}, {"data": [[16.0, 80.0], [9.0, 316.0], [13.0, 383.0]], "isOverall": false, "label": "Failures", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 63.0, "title": "Response Time Vs Request"}},
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
    data: {"result": {"minY": 0.0, "minX": 6.0, "maxY": 575.0, "series": [{"data": [[8.0, 297.5], [9.0, 295.5], [10.0, 296.0], [42.0, 461.0], [11.0, 575.0], [12.0, 288.5], [50.0, 517.0], [13.0, 292.0], [57.0, 477.0], [14.0, 289.5], [15.0, 288.0], [63.0, 474.0], [16.0, 295.0], [6.0, 282.0], [7.0, 300.0]], "isOverall": false, "label": "Successes", "isController": false}, {"data": [[16.0, 0.0], [9.0, 0.0], [13.0, 0.0]], "isOverall": false, "label": "Failures", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 63.0, "title": "Latencies Vs Request"}},
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
        data: {"result": {"minY": 5.733333333333333, "minX": 1.79222076E12, "maxY": 9.266666666666667, "series": [{"data": [[1.79222082E12, 9.266666666666667], [1.79222076E12, 5.733333333333333]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222082E12, "title": "Hits Per Second"}},
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
        data: {"result": {"minY": 0.05, "minX": 1.79222076E12, "maxY": 9.25, "series": [{"data": [[1.79222082E12, 9.25], [1.79222076E12, 5.7]], "isOverall": false, "label": "200", "isController": false}, {"data": [[1.79222082E12, 0.05]], "isOverall": false, "label": "Non HTTP response code: java.net.SocketException", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79222082E12, "title": "Codes Per Second"}},
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
        data: {"result": {"minY": 0.05, "minX": 1.79222076E12, "maxY": 9.25, "series": [{"data": [[1.79222082E12, 9.25], [1.79222076E12, 5.7]], "isOverall": false, "label": "API Request-success", "isController": false}, {"data": [[1.79222082E12, 0.05]], "isOverall": false, "label": "API Request-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222082E12, "title": "Transactions Per Second"}},
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
        data: {"result": {"minY": 0.05, "minX": 1.79222076E12, "maxY": 9.25, "series": [{"data": [[1.79222082E12, 9.25], [1.79222076E12, 5.7]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [[1.79222082E12, 0.05]], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79222082E12, "title": "Total Transactions Per Second"}},
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

