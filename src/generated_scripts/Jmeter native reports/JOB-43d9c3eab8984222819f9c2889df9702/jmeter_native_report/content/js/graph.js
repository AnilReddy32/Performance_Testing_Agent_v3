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
        data: {"result": {"minY": 77.0, "minX": 0.0, "maxY": 2970.0, "series": [{"data": [[0.0, 77.0], [0.1, 77.0], [0.2, 77.0], [0.3, 77.0], [0.4, 78.0], [0.5, 78.0], [0.6, 78.0], [0.7, 79.0], [0.8, 79.0], [0.9, 79.0], [1.0, 79.0], [1.1, 80.0], [1.2, 81.0], [1.3, 81.0], [1.4, 82.0], [1.5, 82.0], [1.6, 82.0], [1.7, 83.0], [1.8, 83.0], [1.9, 83.0], [2.0, 83.0], [2.1, 83.0], [2.2, 84.0], [2.3, 84.0], [2.4, 84.0], [2.5, 84.0], [2.6, 85.0], [2.7, 85.0], [2.8, 85.0], [2.9, 87.0], [3.0, 87.0], [3.1, 87.0], [3.2, 87.0], [3.3, 87.0], [3.4, 87.0], [3.5, 87.0], [3.6, 88.0], [3.7, 88.0], [3.8, 88.0], [3.9, 89.0], [4.0, 89.0], [4.1, 89.0], [4.2, 89.0], [4.3, 89.0], [4.4, 89.0], [4.5, 89.0], [4.6, 89.0], [4.7, 90.0], [4.8, 90.0], [4.9, 90.0], [5.0, 90.0], [5.1, 90.0], [5.2, 90.0], [5.3, 90.0], [5.4, 90.0], [5.5, 90.0], [5.6, 91.0], [5.7, 91.0], [5.8, 91.0], [5.9, 92.0], [6.0, 92.0], [6.1, 92.0], [6.2, 92.0], [6.3, 92.0], [6.4, 92.0], [6.5, 92.0], [6.6, 93.0], [6.7, 93.0], [6.8, 93.0], [6.9, 93.0], [7.0, 93.0], [7.1, 94.0], [7.2, 94.0], [7.3, 94.0], [7.4, 94.0], [7.5, 94.0], [7.6, 94.0], [7.7, 94.0], [7.8, 94.0], [7.9, 95.0], [8.0, 95.0], [8.1, 95.0], [8.2, 95.0], [8.3, 95.0], [8.4, 95.0], [8.5, 95.0], [8.6, 95.0], [8.7, 95.0], [8.8, 95.0], [8.9, 95.0], [9.0, 95.0], [9.1, 96.0], [9.2, 96.0], [9.3, 96.0], [9.4, 96.0], [9.5, 96.0], [9.6, 96.0], [9.7, 97.0], [9.8, 97.0], [9.9, 97.0], [10.0, 97.0], [10.1, 97.0], [10.2, 97.0], [10.3, 97.0], [10.4, 97.0], [10.5, 97.0], [10.6, 97.0], [10.7, 97.0], [10.8, 97.0], [10.9, 98.0], [11.0, 98.0], [11.1, 98.0], [11.2, 98.0], [11.3, 98.0], [11.4, 98.0], [11.5, 98.0], [11.6, 98.0], [11.7, 98.0], [11.8, 99.0], [11.9, 99.0], [12.0, 99.0], [12.1, 99.0], [12.2, 99.0], [12.3, 99.0], [12.4, 99.0], [12.5, 99.0], [12.6, 99.0], [12.7, 99.0], [12.8, 99.0], [12.9, 99.0], [13.0, 99.0], [13.1, 99.0], [13.2, 99.0], [13.3, 100.0], [13.4, 100.0], [13.5, 100.0], [13.6, 100.0], [13.7, 100.0], [13.8, 100.0], [13.9, 101.0], [14.0, 101.0], [14.1, 101.0], [14.2, 101.0], [14.3, 102.0], [14.4, 102.0], [14.5, 102.0], [14.6, 102.0], [14.7, 102.0], [14.8, 102.0], [14.9, 102.0], [15.0, 102.0], [15.1, 103.0], [15.2, 103.0], [15.3, 103.0], [15.4, 103.0], [15.5, 103.0], [15.6, 103.0], [15.7, 103.0], [15.8, 104.0], [15.9, 104.0], [16.0, 104.0], [16.1, 105.0], [16.2, 105.0], [16.3, 105.0], [16.4, 106.0], [16.5, 106.0], [16.6, 106.0], [16.7, 106.0], [16.8, 106.0], [16.9, 106.0], [17.0, 106.0], [17.1, 106.0], [17.2, 106.0], [17.3, 108.0], [17.4, 108.0], [17.5, 108.0], [17.6, 109.0], [17.7, 109.0], [17.8, 109.0], [17.9, 111.0], [18.0, 111.0], [18.1, 111.0], [18.2, 111.0], [18.3, 113.0], [18.4, 115.0], [18.5, 115.0], [18.6, 115.0], [18.7, 115.0], [18.8, 115.0], [18.9, 115.0], [19.0, 115.0], [19.1, 116.0], [19.2, 116.0], [19.3, 117.0], [19.4, 117.0], [19.5, 117.0], [19.6, 119.0], [19.7, 119.0], [19.8, 121.0], [19.9, 121.0], [20.0, 121.0], [20.1, 121.0], [20.2, 121.0], [20.3, 123.0], [20.4, 123.0], [20.5, 188.0], [20.6, 189.0], [20.7, 189.0], [20.8, 193.0], [20.9, 193.0], [21.0, 193.0], [21.1, 193.0], [21.2, 193.0], [21.3, 195.0], [21.4, 195.0], [21.5, 196.0], [21.6, 198.0], [21.7, 198.0], [21.8, 198.0], [21.9, 198.0], [22.0, 198.0], [22.1, 200.0], [22.2, 200.0], [22.3, 200.0], [22.4, 200.0], [22.5, 200.0], [22.6, 201.0], [22.7, 201.0], [22.8, 201.0], [22.9, 201.0], [23.0, 201.0], [23.1, 201.0], [23.2, 201.0], [23.3, 201.0], [23.4, 201.0], [23.5, 201.0], [23.6, 202.0], [23.7, 202.0], [23.8, 202.0], [23.9, 202.0], [24.0, 202.0], [24.1, 202.0], [24.2, 202.0], [24.3, 202.0], [24.4, 202.0], [24.5, 203.0], [24.6, 203.0], [24.7, 203.0], [24.8, 203.0], [24.9, 203.0], [25.0, 204.0], [25.1, 204.0], [25.2, 204.0], [25.3, 204.0], [25.4, 204.0], [25.5, 204.0], [25.6, 204.0], [25.7, 204.0], [25.8, 204.0], [25.9, 204.0], [26.0, 204.0], [26.1, 204.0], [26.2, 204.0], [26.3, 204.0], [26.4, 204.0], [26.5, 205.0], [26.6, 205.0], [26.7, 205.0], [26.8, 205.0], [26.9, 205.0], [27.0, 206.0], [27.1, 206.0], [27.2, 206.0], [27.3, 206.0], [27.4, 206.0], [27.5, 206.0], [27.6, 206.0], [27.7, 206.0], [27.8, 206.0], [27.9, 206.0], [28.0, 207.0], [28.1, 207.0], [28.2, 207.0], [28.3, 207.0], [28.4, 207.0], [28.5, 207.0], [28.6, 207.0], [28.7, 207.0], [28.8, 207.0], [28.9, 207.0], [29.0, 207.0], [29.1, 207.0], [29.2, 207.0], [29.3, 207.0], [29.4, 207.0], [29.5, 208.0], [29.6, 208.0], [29.7, 208.0], [29.8, 208.0], [29.9, 208.0], [30.0, 208.0], [30.1, 208.0], [30.2, 208.0], [30.3, 208.0], [30.4, 208.0], [30.5, 208.0], [30.6, 208.0], [30.7, 208.0], [30.8, 208.0], [30.9, 208.0], [31.0, 209.0], [31.1, 209.0], [31.2, 209.0], [31.3, 209.0], [31.4, 209.0], [31.5, 209.0], [31.6, 209.0], [31.7, 209.0], [31.8, 209.0], [31.9, 209.0], [32.0, 209.0], [32.1, 209.0], [32.2, 209.0], [32.3, 209.0], [32.4, 209.0], [32.5, 209.0], [32.6, 209.0], [32.7, 209.0], [32.8, 209.0], [32.9, 209.0], [33.0, 210.0], [33.1, 210.0], [33.2, 210.0], [33.3, 210.0], [33.4, 210.0], [33.5, 210.0], [33.6, 210.0], [33.7, 210.0], [33.8, 210.0], [33.9, 210.0], [34.0, 210.0], [34.1, 210.0], [34.2, 210.0], [34.3, 210.0], [34.4, 210.0], [34.5, 210.0], [34.6, 210.0], [34.7, 211.0], [34.8, 211.0], [34.9, 211.0], [35.0, 211.0], [35.1, 211.0], [35.2, 211.0], [35.3, 211.0], [35.4, 211.0], [35.5, 211.0], [35.6, 211.0], [35.7, 211.0], [35.8, 211.0], [35.9, 211.0], [36.0, 211.0], [36.1, 211.0], [36.2, 212.0], [36.3, 212.0], [36.4, 212.0], [36.5, 212.0], [36.6, 212.0], [36.7, 212.0], [36.8, 212.0], [36.9, 212.0], [37.0, 212.0], [37.1, 212.0], [37.2, 212.0], [37.3, 212.0], [37.4, 212.0], [37.5, 212.0], [37.6, 212.0], [37.7, 212.0], [37.8, 212.0], [37.9, 212.0], [38.0, 212.0], [38.1, 212.0], [38.2, 212.0], [38.3, 212.0], [38.4, 212.0], [38.5, 213.0], [38.6, 213.0], [38.7, 213.0], [38.8, 213.0], [38.9, 213.0], [39.0, 213.0], [39.1, 213.0], [39.2, 213.0], [39.3, 213.0], [39.4, 213.0], [39.5, 213.0], [39.6, 213.0], [39.7, 213.0], [39.8, 213.0], [39.9, 213.0], [40.0, 213.0], [40.1, 213.0], [40.2, 213.0], [40.3, 213.0], [40.4, 213.0], [40.5, 214.0], [40.6, 214.0], [40.7, 214.0], [40.8, 214.0], [40.9, 214.0], [41.0, 214.0], [41.1, 214.0], [41.2, 214.0], [41.3, 214.0], [41.4, 214.0], [41.5, 214.0], [41.6, 214.0], [41.7, 214.0], [41.8, 214.0], [41.9, 214.0], [42.0, 214.0], [42.1, 214.0], [42.2, 214.0], [42.3, 214.0], [42.4, 214.0], [42.5, 214.0], [42.6, 214.0], [42.7, 214.0], [42.8, 214.0], [42.9, 214.0], [43.0, 214.0], [43.1, 214.0], [43.2, 214.0], [43.3, 214.0], [43.4, 214.0], [43.5, 214.0], [43.6, 214.0], [43.7, 214.0], [43.8, 214.0], [43.9, 214.0], [44.0, 214.0], [44.1, 214.0], [44.2, 214.0], [44.3, 214.0], [44.4, 214.0], [44.5, 215.0], [44.6, 215.0], [44.7, 215.0], [44.8, 215.0], [44.9, 215.0], [45.0, 215.0], [45.1, 215.0], [45.2, 215.0], [45.3, 215.0], [45.4, 215.0], [45.5, 215.0], [45.6, 215.0], [45.7, 215.0], [45.8, 215.0], [45.9, 215.0], [46.0, 215.0], [46.1, 215.0], [46.2, 215.0], [46.3, 215.0], [46.4, 215.0], [46.5, 215.0], [46.6, 215.0], [46.7, 215.0], [46.8, 215.0], [46.9, 215.0], [47.0, 215.0], [47.1, 215.0], [47.2, 216.0], [47.3, 216.0], [47.4, 216.0], [47.5, 216.0], [47.6, 216.0], [47.7, 216.0], [47.8, 216.0], [47.9, 216.0], [48.0, 216.0], [48.1, 216.0], [48.2, 216.0], [48.3, 216.0], [48.4, 216.0], [48.5, 216.0], [48.6, 216.0], [48.7, 216.0], [48.8, 216.0], [48.9, 216.0], [49.0, 216.0], [49.1, 216.0], [49.2, 217.0], [49.3, 217.0], [49.4, 217.0], [49.5, 217.0], [49.6, 217.0], [49.7, 217.0], [49.8, 217.0], [49.9, 217.0], [50.0, 217.0], [50.1, 217.0], [50.2, 217.0], [50.3, 217.0], [50.4, 217.0], [50.5, 217.0], [50.6, 217.0], [50.7, 217.0], [50.8, 217.0], [50.9, 217.0], [51.0, 217.0], [51.1, 217.0], [51.2, 218.0], [51.3, 218.0], [51.4, 218.0], [51.5, 218.0], [51.6, 218.0], [51.7, 218.0], [51.8, 218.0], [51.9, 218.0], [52.0, 218.0], [52.1, 218.0], [52.2, 218.0], [52.3, 218.0], [52.4, 218.0], [52.5, 218.0], [52.6, 218.0], [52.7, 218.0], [52.8, 218.0], [52.9, 218.0], [53.0, 218.0], [53.1, 218.0], [53.2, 218.0], [53.3, 218.0], [53.4, 218.0], [53.5, 218.0], [53.6, 218.0], [53.7, 218.0], [53.8, 218.0], [53.9, 218.0], [54.0, 218.0], [54.1, 218.0], [54.2, 218.0], [54.3, 218.0], [54.4, 219.0], [54.5, 219.0], [54.6, 219.0], [54.7, 219.0], [54.8, 219.0], [54.9, 219.0], [55.0, 219.0], [55.1, 219.0], [55.2, 219.0], [55.3, 219.0], [55.4, 219.0], [55.5, 219.0], [55.6, 219.0], [55.7, 219.0], [55.8, 219.0], [55.9, 219.0], [56.0, 219.0], [56.1, 219.0], [56.2, 219.0], [56.3, 219.0], [56.4, 219.0], [56.5, 219.0], [56.6, 219.0], [56.7, 219.0], [56.8, 219.0], [56.9, 219.0], [57.0, 219.0], [57.1, 219.0], [57.2, 219.0], [57.3, 219.0], [57.4, 220.0], [57.5, 220.0], [57.6, 220.0], [57.7, 220.0], [57.8, 220.0], [57.9, 220.0], [58.0, 220.0], [58.1, 220.0], [58.2, 220.0], [58.3, 220.0], [58.4, 220.0], [58.5, 220.0], [58.6, 220.0], [58.7, 220.0], [58.8, 220.0], [58.9, 220.0], [59.0, 220.0], [59.1, 220.0], [59.2, 220.0], [59.3, 220.0], [59.4, 220.0], [59.5, 220.0], [59.6, 220.0], [59.7, 221.0], [59.8, 221.0], [59.9, 221.0], [60.0, 221.0], [60.1, 221.0], [60.2, 221.0], [60.3, 221.0], [60.4, 221.0], [60.5, 221.0], [60.6, 221.0], [60.7, 221.0], [60.8, 221.0], [60.9, 221.0], [61.0, 221.0], [61.1, 221.0], [61.2, 221.0], [61.3, 221.0], [61.4, 221.0], [61.5, 221.0], [61.6, 221.0], [61.7, 221.0], [61.8, 221.0], [61.9, 221.0], [62.0, 221.0], [62.1, 221.0], [62.2, 221.0], [62.3, 221.0], [62.4, 222.0], [62.5, 222.0], [62.6, 222.0], [62.7, 222.0], [62.8, 222.0], [62.9, 222.0], [63.0, 222.0], [63.1, 222.0], [63.2, 222.0], [63.3, 222.0], [63.4, 222.0], [63.5, 222.0], [63.6, 222.0], [63.7, 222.0], [63.8, 222.0], [63.9, 222.0], [64.0, 222.0], [64.1, 223.0], [64.2, 223.0], [64.3, 223.0], [64.4, 223.0], [64.5, 223.0], [64.6, 223.0], [64.7, 223.0], [64.8, 223.0], [64.9, 223.0], [65.0, 223.0], [65.1, 223.0], [65.2, 223.0], [65.3, 223.0], [65.4, 223.0], [65.5, 223.0], [65.6, 223.0], [65.7, 223.0], [65.8, 223.0], [65.9, 223.0], [66.0, 223.0], [66.1, 223.0], [66.2, 223.0], [66.3, 223.0], [66.4, 223.0], [66.5, 223.0], [66.6, 223.0], [66.7, 223.0], [66.8, 223.0], [66.9, 224.0], [67.0, 224.0], [67.1, 224.0], [67.2, 224.0], [67.3, 224.0], [67.4, 224.0], [67.5, 224.0], [67.6, 224.0], [67.7, 224.0], [67.8, 224.0], [67.9, 224.0], [68.0, 224.0], [68.1, 224.0], [68.2, 224.0], [68.3, 224.0], [68.4, 224.0], [68.5, 224.0], [68.6, 224.0], [68.7, 224.0], [68.8, 224.0], [68.9, 224.0], [69.0, 224.0], [69.1, 224.0], [69.2, 224.0], [69.3, 224.0], [69.4, 224.0], [69.5, 224.0], [69.6, 224.0], [69.7, 224.0], [69.8, 224.0], [69.9, 224.0], [70.0, 224.0], [70.1, 224.0], [70.2, 224.0], [70.3, 224.0], [70.4, 224.0], [70.5, 225.0], [70.6, 225.0], [70.7, 225.0], [70.8, 225.0], [70.9, 225.0], [71.0, 225.0], [71.1, 226.0], [71.2, 226.0], [71.3, 226.0], [71.4, 226.0], [71.5, 226.0], [71.6, 226.0], [71.7, 226.0], [71.8, 226.0], [71.9, 226.0], [72.0, 226.0], [72.1, 226.0], [72.2, 226.0], [72.3, 226.0], [72.4, 226.0], [72.5, 226.0], [72.6, 226.0], [72.7, 226.0], [72.8, 226.0], [72.9, 226.0], [73.0, 226.0], [73.1, 227.0], [73.2, 227.0], [73.3, 227.0], [73.4, 227.0], [73.5, 227.0], [73.6, 227.0], [73.7, 227.0], [73.8, 227.0], [73.9, 227.0], [74.0, 227.0], [74.1, 227.0], [74.2, 227.0], [74.3, 227.0], [74.4, 227.0], [74.5, 227.0], [74.6, 227.0], [74.7, 227.0], [74.8, 228.0], [74.9, 228.0], [75.0, 228.0], [75.1, 228.0], [75.2, 228.0], [75.3, 228.0], [75.4, 228.0], [75.5, 228.0], [75.6, 228.0], [75.7, 228.0], [75.8, 228.0], [75.9, 228.0], [76.0, 228.0], [76.1, 228.0], [76.2, 228.0], [76.3, 228.0], [76.4, 228.0], [76.5, 228.0], [76.6, 228.0], [76.7, 228.0], [76.8, 229.0], [76.9, 229.0], [77.0, 229.0], [77.1, 229.0], [77.2, 229.0], [77.3, 229.0], [77.4, 229.0], [77.5, 229.0], [77.6, 229.0], [77.7, 229.0], [77.8, 229.0], [77.9, 229.0], [78.0, 229.0], [78.1, 229.0], [78.2, 229.0], [78.3, 229.0], [78.4, 229.0], [78.5, 230.0], [78.6, 230.0], [78.7, 230.0], [78.8, 230.0], [78.9, 230.0], [79.0, 230.0], [79.1, 230.0], [79.2, 230.0], [79.3, 230.0], [79.4, 230.0], [79.5, 230.0], [79.6, 230.0], [79.7, 230.0], [79.8, 230.0], [79.9, 230.0], [80.0, 231.0], [80.1, 231.0], [80.2, 231.0], [80.3, 231.0], [80.4, 231.0], [80.5, 231.0], [80.6, 231.0], [80.7, 231.0], [80.8, 231.0], [80.9, 231.0], [81.0, 231.0], [81.1, 231.0], [81.2, 231.0], [81.3, 231.0], [81.4, 231.0], [81.5, 231.0], [81.6, 231.0], [81.7, 231.0], [81.8, 231.0], [81.9, 231.0], [82.0, 231.0], [82.1, 231.0], [82.2, 231.0], [82.3, 232.0], [82.4, 232.0], [82.5, 232.0], [82.6, 232.0], [82.7, 232.0], [82.8, 232.0], [82.9, 232.0], [83.0, 232.0], [83.1, 232.0], [83.2, 232.0], [83.3, 232.0], [83.4, 232.0], [83.5, 233.0], [83.6, 233.0], [83.7, 233.0], [83.8, 233.0], [83.9, 233.0], [84.0, 233.0], [84.1, 233.0], [84.2, 233.0], [84.3, 233.0], [84.4, 233.0], [84.5, 234.0], [84.6, 234.0], [84.7, 234.0], [84.8, 234.0], [84.9, 234.0], [85.0, 234.0], [85.1, 234.0], [85.2, 234.0], [85.3, 234.0], [85.4, 234.0], [85.5, 235.0], [85.6, 235.0], [85.7, 235.0], [85.8, 235.0], [85.9, 235.0], [86.0, 235.0], [86.1, 235.0], [86.2, 236.0], [86.3, 236.0], [86.4, 236.0], [86.5, 236.0], [86.6, 236.0], [86.7, 236.0], [86.8, 237.0], [86.9, 237.0], [87.0, 237.0], [87.1, 237.0], [87.2, 237.0], [87.3, 237.0], [87.4, 237.0], [87.5, 237.0], [87.6, 237.0], [87.7, 238.0], [87.8, 238.0], [87.9, 238.0], [88.0, 239.0], [88.1, 239.0], [88.2, 239.0], [88.3, 239.0], [88.4, 239.0], [88.5, 240.0], [88.6, 240.0], [88.7, 240.0], [88.8, 242.0], [88.9, 242.0], [89.0, 243.0], [89.1, 243.0], [89.2, 244.0], [89.3, 244.0], [89.4, 244.0], [89.5, 245.0], [89.6, 245.0], [89.7, 245.0], [89.8, 245.0], [89.9, 245.0], [90.0, 246.0], [90.1, 246.0], [90.2, 246.0], [90.3, 246.0], [90.4, 246.0], [90.5, 247.0], [90.6, 247.0], [90.7, 247.0], [90.8, 247.0], [90.9, 247.0], [91.0, 247.0], [91.1, 247.0], [91.2, 248.0], [91.3, 248.0], [91.4, 248.0], [91.5, 249.0], [91.6, 249.0], [91.7, 249.0], [91.8, 249.0], [91.9, 250.0], [92.0, 250.0], [92.1, 250.0], [92.2, 251.0], [92.3, 251.0], [92.4, 251.0], [92.5, 252.0], [92.6, 252.0], [92.7, 252.0], [92.8, 252.0], [92.9, 252.0], [93.0, 253.0], [93.1, 253.0], [93.2, 253.0], [93.3, 253.0], [93.4, 254.0], [93.5, 254.0], [93.6, 254.0], [93.7, 254.0], [93.8, 254.0], [93.9, 255.0], [94.0, 255.0], [94.1, 255.0], [94.2, 255.0], [94.3, 255.0], [94.4, 255.0], [94.5, 255.0], [94.6, 255.0], [94.7, 256.0], [94.8, 256.0], [94.9, 257.0], [95.0, 257.0], [95.1, 257.0], [95.2, 258.0], [95.3, 258.0], [95.4, 259.0], [95.5, 259.0], [95.6, 259.0], [95.7, 259.0], [95.8, 259.0], [95.9, 261.0], [96.0, 263.0], [96.1, 263.0], [96.2, 263.0], [96.3, 263.0], [96.4, 263.0], [96.5, 265.0], [96.6, 265.0], [96.7, 268.0], [96.8, 268.0], [96.9, 268.0], [97.0, 272.0], [97.1, 272.0], [97.2, 303.0], [97.3, 303.0], [97.4, 317.0], [97.5, 322.0], [97.6, 322.0], [97.7, 341.0], [97.8, 341.0], [97.9, 624.0], [98.0, 630.0], [98.1, 630.0], [98.2, 635.0], [98.3, 635.0], [98.4, 636.0], [98.5, 637.0], [98.6, 637.0], [98.7, 644.0], [98.8, 644.0], [98.9, 647.0], [99.0, 650.0], [99.1, 650.0], [99.2, 660.0], [99.3, 660.0], [99.4, 667.0], [99.5, 738.0], [99.6, 738.0], [99.7, 846.0], [99.8, 846.0], [99.9, 2970.0], [100.0, 2970.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
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
        data: {"result": {"minY": 1.0, "minX": 0.0, "maxY": 449.0, "series": [{"data": [[0.0, 79.0], [300.0, 4.0], [600.0, 10.0], [700.0, 1.0], [2900.0, 1.0], [100.0, 53.0], [800.0, 1.0], [200.0, 449.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 2900.0, "title": "Response Time Distribution"}},
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
        data: {"result": {"minY": 1.0, "minX": 0.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 585.0, "series": [{"data": [[0.0, 585.0]], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [[1.0, 12.0]], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [[2.0, 1.0]], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 2.0, "title": "Synthetic Response Times Distribution"}},
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
        data: {"result": {"minY": 11.990196078431378, "minX": 1.79215272E12, "maxY": 14.788306451612904, "series": [{"data": [[1.79215272E12, 11.990196078431378], [1.79215278E12, 14.788306451612904]], "isOverall": false, "label": "Virtual Users", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79215278E12, "title": "Active Threads Over Time"}},
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
        data: {"result": {"minY": 157.0, "minX": 1.0, "maxY": 325.3333333333333, "series": [{"data": [[2.0, 265.5], [8.0, 157.0], [9.0, 325.3333333333333], [10.0, 319.75], [11.0, 278.2], [3.0, 268.0], [12.0, 197.75], [13.0, 292.2], [14.0, 280.4], [15.0, 204.87546468401487], [4.0, 294.4], [1.0, 228.0], [5.0, 169.6], [6.0, 312.5], [7.0, 275.4]], "isOverall": false, "label": "API Request", "isController": false}, {"data": [[14.31103678929766, 210.99163879598666]], "isOverall": false, "label": "API Request-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 15.0, "title": "Time VS Threads"}},
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
        data : {"result": {"minY": 253.3, "minX": 1.79215272E12, "maxY": 20985.55, "series": [{"data": [[1.79215272E12, 4316.316666666667], [1.79215278E12, 20985.55]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.79215272E12, 253.3], [1.79215278E12, 1231.7333333333333]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79215278E12, "title": "Bytes Throughput Over Time"}},
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
        data: {"result": {"minY": 203.62701612903226, "minX": 1.79215272E12, "maxY": 246.80392156862746, "series": [{"data": [[1.79215272E12, 246.80392156862746], [1.79215278E12, 203.62701612903226]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79215278E12, "title": "Response Time Over Time"}},
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
        data: {"result": {"minY": 202.73991935483858, "minX": 1.79215272E12, "maxY": 244.75490196078434, "series": [{"data": [[1.79215272E12, 244.75490196078434], [1.79215278E12, 202.73991935483858]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79215278E12, "title": "Latencies Over Time"}},
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
        data: {"result": {"minY": 0.0, "minX": 1.79215272E12, "maxY": 57.970588235294116, "series": [{"data": [[1.79215272E12, 57.970588235294116], [1.79215278E12, 0.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79215278E12, "title": "Connect Time Over Time"}},
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
        data: {"result": {"minY": 77.0, "minX": 1.79215272E12, "maxY": 2970.0, "series": [{"data": [[1.79215272E12, 846.0], [1.79215278E12, 2970.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.79215272E12, 77.0], [1.79215278E12, 77.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.79215272E12, 633.5], [1.79215278E12, 239.0]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.79215272E12, 842.7599999999999], [1.79215278E12, 268.1199999999999]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.79215272E12, 219.0], [1.79215278E12, 217.0]], "isOverall": false, "label": "Median", "isController": false}, {"data": [[1.79215272E12, 649.55], [1.79215278E12, 252.0]], "isOverall": false, "label": "95th percentile", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79215278E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
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
    data: {"result": {"minY": 214.0, "minX": 6.0, "maxY": 227.0, "series": [{"data": [[8.0, 218.0], [9.0, 218.0], [10.0, 215.0], [11.0, 217.0], [12.0, 218.5], [6.0, 227.0], [13.0, 214.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 13.0, "title": "Response Time Vs Request"}},
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
    data: {"result": {"minY": 210.0, "minX": 6.0, "maxY": 226.5, "series": [{"data": [[8.0, 215.0], [9.0, 217.0], [10.0, 214.0], [11.0, 217.0], [12.0, 218.0], [6.0, 226.5], [13.0, 210.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 13.0, "title": "Latencies Vs Request"}},
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
        data: {"result": {"minY": 1.7333333333333334, "minX": 1.79215272E12, "maxY": 8.233333333333333, "series": [{"data": [[1.79215272E12, 1.7333333333333334], [1.79215278E12, 8.233333333333333]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79215278E12, "title": "Hits Per Second"}},
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
        data: {"result": {"minY": 1.7, "minX": 1.79215272E12, "maxY": 8.266666666666667, "series": [{"data": [[1.79215272E12, 1.7], [1.79215278E12, 8.266666666666667]], "isOverall": false, "label": "200", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79215278E12, "title": "Codes Per Second"}},
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
        data: {"result": {"minY": 1.7, "minX": 1.79215272E12, "maxY": 8.266666666666667, "series": [{"data": [[1.79215272E12, 1.7], [1.79215278E12, 8.266666666666667]], "isOverall": false, "label": "API Request-success", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79215278E12, "title": "Transactions Per Second"}},
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
        data: {"result": {"minY": 1.7, "minX": 1.79215272E12, "maxY": 8.266666666666667, "series": [{"data": [[1.79215272E12, 1.7], [1.79215278E12, 8.266666666666667]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79215278E12, "title": "Total Transactions Per Second"}},
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

