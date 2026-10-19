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
        data: {"result": {"minY": 356.0, "minX": 0.0, "maxY": 9166.0, "series": [{"data": [[0.0, 356.0], [0.1, 356.0], [0.2, 394.0], [0.3, 402.0], [0.4, 403.0], [0.5, 409.0], [0.6, 413.0], [0.7, 413.0], [0.8, 418.0], [0.9, 419.0], [1.0, 425.0], [1.1, 427.0], [1.2, 427.0], [1.3, 433.0], [1.4, 433.0], [1.5, 434.0], [1.6, 437.0], [1.7, 439.0], [1.8, 442.0], [1.9, 443.0], [2.0, 445.0], [2.1, 446.0], [2.2, 449.0], [2.3, 449.0], [2.4, 451.0], [2.5, 451.0], [2.6, 452.0], [2.7, 452.0], [2.8, 454.0], [2.9, 455.0], [3.0, 455.0], [3.1, 455.0], [3.2, 456.0], [3.3, 456.0], [3.4, 456.0], [3.5, 457.0], [3.6, 457.0], [3.7, 457.0], [3.8, 458.0], [3.9, 458.0], [4.0, 459.0], [4.1, 460.0], [4.2, 461.0], [4.3, 461.0], [4.4, 462.0], [4.5, 462.0], [4.6, 464.0], [4.7, 464.0], [4.8, 464.0], [4.9, 465.0], [5.0, 466.0], [5.1, 466.0], [5.2, 468.0], [5.3, 468.0], [5.4, 468.0], [5.5, 469.0], [5.6, 469.0], [5.7, 469.0], [5.8, 470.0], [5.9, 470.0], [6.0, 470.0], [6.1, 470.0], [6.2, 471.0], [6.3, 472.0], [6.4, 472.0], [6.5, 474.0], [6.6, 474.0], [6.7, 474.0], [6.8, 474.0], [6.9, 475.0], [7.0, 476.0], [7.1, 476.0], [7.2, 477.0], [7.3, 477.0], [7.4, 478.0], [7.5, 478.0], [7.6, 478.0], [7.7, 480.0], [7.8, 480.0], [7.9, 480.0], [8.0, 480.0], [8.1, 480.0], [8.2, 481.0], [8.3, 482.0], [8.4, 482.0], [8.5, 482.0], [8.6, 483.0], [8.7, 483.0], [8.8, 484.0], [8.9, 484.0], [9.0, 484.0], [9.1, 484.0], [9.2, 484.0], [9.3, 484.0], [9.4, 485.0], [9.5, 486.0], [9.6, 486.0], [9.7, 487.0], [9.8, 487.0], [9.9, 489.0], [10.0, 489.0], [10.1, 489.0], [10.2, 490.0], [10.3, 490.0], [10.4, 491.0], [10.5, 491.0], [10.6, 491.0], [10.7, 493.0], [10.8, 493.0], [10.9, 494.0], [11.0, 494.0], [11.1, 494.0], [11.2, 494.0], [11.3, 494.0], [11.4, 495.0], [11.5, 495.0], [11.6, 496.0], [11.7, 496.0], [11.8, 496.0], [11.9, 496.0], [12.0, 497.0], [12.1, 497.0], [12.2, 498.0], [12.3, 498.0], [12.4, 498.0], [12.5, 499.0], [12.6, 499.0], [12.7, 499.0], [12.8, 500.0], [12.9, 500.0], [13.0, 500.0], [13.1, 501.0], [13.2, 501.0], [13.3, 501.0], [13.4, 501.0], [13.5, 501.0], [13.6, 502.0], [13.7, 502.0], [13.8, 502.0], [13.9, 502.0], [14.0, 503.0], [14.1, 503.0], [14.2, 503.0], [14.3, 503.0], [14.4, 503.0], [14.5, 503.0], [14.6, 504.0], [14.7, 506.0], [14.8, 506.0], [14.9, 507.0], [15.0, 508.0], [15.1, 509.0], [15.2, 509.0], [15.3, 510.0], [15.4, 511.0], [15.5, 511.0], [15.6, 511.0], [15.7, 511.0], [15.8, 511.0], [15.9, 512.0], [16.0, 513.0], [16.1, 513.0], [16.2, 514.0], [16.3, 514.0], [16.4, 515.0], [16.5, 515.0], [16.6, 515.0], [16.7, 515.0], [16.8, 515.0], [16.9, 516.0], [17.0, 516.0], [17.1, 517.0], [17.2, 517.0], [17.3, 517.0], [17.4, 518.0], [17.5, 518.0], [17.6, 518.0], [17.7, 518.0], [17.8, 518.0], [17.9, 518.0], [18.0, 519.0], [18.1, 519.0], [18.2, 519.0], [18.3, 519.0], [18.4, 519.0], [18.5, 520.0], [18.6, 520.0], [18.7, 521.0], [18.8, 521.0], [18.9, 521.0], [19.0, 521.0], [19.1, 522.0], [19.2, 522.0], [19.3, 522.0], [19.4, 523.0], [19.5, 523.0], [19.6, 523.0], [19.7, 524.0], [19.8, 524.0], [19.9, 524.0], [20.0, 524.0], [20.1, 524.0], [20.2, 525.0], [20.3, 525.0], [20.4, 525.0], [20.5, 525.0], [20.6, 526.0], [20.7, 526.0], [20.8, 526.0], [20.9, 526.0], [21.0, 526.0], [21.1, 527.0], [21.2, 527.0], [21.3, 528.0], [21.4, 528.0], [21.5, 529.0], [21.6, 529.0], [21.7, 529.0], [21.8, 530.0], [21.9, 530.0], [22.0, 530.0], [22.1, 530.0], [22.2, 530.0], [22.3, 530.0], [22.4, 532.0], [22.5, 532.0], [22.6, 532.0], [22.7, 533.0], [22.8, 533.0], [22.9, 533.0], [23.0, 533.0], [23.1, 534.0], [23.2, 534.0], [23.3, 534.0], [23.4, 534.0], [23.5, 534.0], [23.6, 535.0], [23.7, 536.0], [23.8, 536.0], [23.9, 536.0], [24.0, 537.0], [24.1, 537.0], [24.2, 538.0], [24.3, 538.0], [24.4, 539.0], [24.5, 539.0], [24.6, 539.0], [24.7, 541.0], [24.8, 541.0], [24.9, 541.0], [25.0, 542.0], [25.1, 543.0], [25.2, 543.0], [25.3, 543.0], [25.4, 543.0], [25.5, 543.0], [25.6, 543.0], [25.7, 543.0], [25.8, 544.0], [25.9, 544.0], [26.0, 544.0], [26.1, 544.0], [26.2, 545.0], [26.3, 546.0], [26.4, 546.0], [26.5, 547.0], [26.6, 547.0], [26.7, 547.0], [26.8, 547.0], [26.9, 547.0], [27.0, 548.0], [27.1, 548.0], [27.2, 548.0], [27.3, 548.0], [27.4, 549.0], [27.5, 549.0], [27.6, 549.0], [27.7, 550.0], [27.8, 550.0], [27.9, 551.0], [28.0, 551.0], [28.1, 551.0], [28.2, 551.0], [28.3, 553.0], [28.4, 553.0], [28.5, 553.0], [28.6, 553.0], [28.7, 553.0], [28.8, 554.0], [28.9, 554.0], [29.0, 554.0], [29.1, 555.0], [29.2, 556.0], [29.3, 556.0], [29.4, 556.0], [29.5, 556.0], [29.6, 556.0], [29.7, 557.0], [29.8, 557.0], [29.9, 558.0], [30.0, 558.0], [30.1, 558.0], [30.2, 558.0], [30.3, 558.0], [30.4, 558.0], [30.5, 558.0], [30.6, 558.0], [30.7, 559.0], [30.8, 559.0], [30.9, 559.0], [31.0, 559.0], [31.1, 559.0], [31.2, 559.0], [31.3, 559.0], [31.4, 560.0], [31.5, 560.0], [31.6, 560.0], [31.7, 560.0], [31.8, 561.0], [31.9, 561.0], [32.0, 561.0], [32.1, 562.0], [32.2, 562.0], [32.3, 562.0], [32.4, 562.0], [32.5, 562.0], [32.6, 563.0], [32.7, 563.0], [32.8, 563.0], [32.9, 563.0], [33.0, 564.0], [33.1, 564.0], [33.2, 564.0], [33.3, 564.0], [33.4, 564.0], [33.5, 564.0], [33.6, 564.0], [33.7, 565.0], [33.8, 565.0], [33.9, 565.0], [34.0, 566.0], [34.1, 566.0], [34.2, 566.0], [34.3, 566.0], [34.4, 566.0], [34.5, 566.0], [34.6, 567.0], [34.7, 567.0], [34.8, 567.0], [34.9, 567.0], [35.0, 567.0], [35.1, 568.0], [35.2, 568.0], [35.3, 568.0], [35.4, 569.0], [35.5, 569.0], [35.6, 569.0], [35.7, 569.0], [35.8, 569.0], [35.9, 569.0], [36.0, 569.0], [36.1, 570.0], [36.2, 570.0], [36.3, 570.0], [36.4, 570.0], [36.5, 570.0], [36.6, 571.0], [36.7, 571.0], [36.8, 571.0], [36.9, 571.0], [37.0, 572.0], [37.1, 572.0], [37.2, 573.0], [37.3, 574.0], [37.4, 574.0], [37.5, 574.0], [37.6, 574.0], [37.7, 574.0], [37.8, 574.0], [37.9, 574.0], [38.0, 575.0], [38.1, 575.0], [38.2, 575.0], [38.3, 575.0], [38.4, 576.0], [38.5, 576.0], [38.6, 576.0], [38.7, 577.0], [38.8, 577.0], [38.9, 577.0], [39.0, 577.0], [39.1, 577.0], [39.2, 577.0], [39.3, 578.0], [39.4, 578.0], [39.5, 578.0], [39.6, 578.0], [39.7, 579.0], [39.8, 579.0], [39.9, 580.0], [40.0, 580.0], [40.1, 580.0], [40.2, 580.0], [40.3, 580.0], [40.4, 580.0], [40.5, 580.0], [40.6, 581.0], [40.7, 581.0], [40.8, 581.0], [40.9, 583.0], [41.0, 584.0], [41.1, 585.0], [41.2, 585.0], [41.3, 585.0], [41.4, 585.0], [41.5, 586.0], [41.6, 587.0], [41.7, 587.0], [41.8, 587.0], [41.9, 587.0], [42.0, 587.0], [42.1, 587.0], [42.2, 588.0], [42.3, 588.0], [42.4, 589.0], [42.5, 590.0], [42.6, 590.0], [42.7, 590.0], [42.8, 590.0], [42.9, 591.0], [43.0, 591.0], [43.1, 591.0], [43.2, 591.0], [43.3, 593.0], [43.4, 593.0], [43.5, 593.0], [43.6, 593.0], [43.7, 594.0], [43.8, 594.0], [43.9, 594.0], [44.0, 595.0], [44.1, 595.0], [44.2, 595.0], [44.3, 595.0], [44.4, 595.0], [44.5, 595.0], [44.6, 595.0], [44.7, 595.0], [44.8, 595.0], [44.9, 596.0], [45.0, 596.0], [45.1, 597.0], [45.2, 597.0], [45.3, 598.0], [45.4, 598.0], [45.5, 598.0], [45.6, 598.0], [45.7, 599.0], [45.8, 599.0], [45.9, 600.0], [46.0, 601.0], [46.1, 601.0], [46.2, 603.0], [46.3, 604.0], [46.4, 605.0], [46.5, 606.0], [46.6, 606.0], [46.7, 606.0], [46.8, 607.0], [46.9, 607.0], [47.0, 608.0], [47.1, 609.0], [47.2, 610.0], [47.3, 610.0], [47.4, 610.0], [47.5, 610.0], [47.6, 612.0], [47.7, 614.0], [47.8, 614.0], [47.9, 614.0], [48.0, 615.0], [48.1, 617.0], [48.2, 618.0], [48.3, 618.0], [48.4, 618.0], [48.5, 619.0], [48.6, 620.0], [48.7, 620.0], [48.8, 621.0], [48.9, 621.0], [49.0, 622.0], [49.1, 623.0], [49.2, 623.0], [49.3, 624.0], [49.4, 624.0], [49.5, 624.0], [49.6, 626.0], [49.7, 626.0], [49.8, 627.0], [49.9, 628.0], [50.0, 631.0], [50.1, 631.0], [50.2, 632.0], [50.3, 633.0], [50.4, 634.0], [50.5, 636.0], [50.6, 637.0], [50.7, 638.0], [50.8, 639.0], [50.9, 641.0], [51.0, 642.0], [51.1, 643.0], [51.2, 643.0], [51.3, 643.0], [51.4, 647.0], [51.5, 649.0], [51.6, 660.0], [51.7, 660.0], [51.8, 662.0], [51.9, 669.0], [52.0, 670.0], [52.1, 677.0], [52.2, 684.0], [52.3, 684.0], [52.4, 685.0], [52.5, 686.0], [52.6, 690.0], [52.7, 692.0], [52.8, 692.0], [52.9, 693.0], [53.0, 695.0], [53.1, 699.0], [53.2, 711.0], [53.3, 716.0], [53.4, 716.0], [53.5, 717.0], [53.6, 718.0], [53.7, 718.0], [53.8, 719.0], [53.9, 723.0], [54.0, 727.0], [54.1, 728.0], [54.2, 729.0], [54.3, 731.0], [54.4, 739.0], [54.5, 739.0], [54.6, 741.0], [54.7, 741.0], [54.8, 741.0], [54.9, 742.0], [55.0, 743.0], [55.1, 744.0], [55.2, 744.0], [55.3, 745.0], [55.4, 750.0], [55.5, 753.0], [55.6, 753.0], [55.7, 754.0], [55.8, 757.0], [55.9, 760.0], [56.0, 764.0], [56.1, 764.0], [56.2, 764.0], [56.3, 765.0], [56.4, 766.0], [56.5, 767.0], [56.6, 770.0], [56.7, 770.0], [56.8, 771.0], [56.9, 773.0], [57.0, 774.0], [57.1, 775.0], [57.2, 778.0], [57.3, 779.0], [57.4, 780.0], [57.5, 783.0], [57.6, 783.0], [57.7, 787.0], [57.8, 787.0], [57.9, 790.0], [58.0, 790.0], [58.1, 792.0], [58.2, 793.0], [58.3, 793.0], [58.4, 795.0], [58.5, 796.0], [58.6, 796.0], [58.7, 796.0], [58.8, 797.0], [58.9, 797.0], [59.0, 803.0], [59.1, 807.0], [59.2, 807.0], [59.3, 808.0], [59.4, 809.0], [59.5, 810.0], [59.6, 812.0], [59.7, 813.0], [59.8, 813.0], [59.9, 813.0], [60.0, 814.0], [60.1, 814.0], [60.2, 814.0], [60.3, 816.0], [60.4, 816.0], [60.5, 820.0], [60.6, 824.0], [60.7, 827.0], [60.8, 828.0], [60.9, 830.0], [61.0, 833.0], [61.1, 835.0], [61.2, 835.0], [61.3, 838.0], [61.4, 840.0], [61.5, 843.0], [61.6, 848.0], [61.7, 853.0], [61.8, 854.0], [61.9, 860.0], [62.0, 861.0], [62.1, 863.0], [62.2, 863.0], [62.3, 863.0], [62.4, 864.0], [62.5, 866.0], [62.6, 872.0], [62.7, 876.0], [62.8, 876.0], [62.9, 878.0], [63.0, 879.0], [63.1, 880.0], [63.2, 884.0], [63.3, 884.0], [63.4, 884.0], [63.5, 886.0], [63.6, 888.0], [63.7, 891.0], [63.8, 893.0], [63.9, 895.0], [64.0, 896.0], [64.1, 896.0], [64.2, 900.0], [64.3, 909.0], [64.4, 910.0], [64.5, 910.0], [64.6, 913.0], [64.7, 913.0], [64.8, 914.0], [64.9, 915.0], [65.0, 917.0], [65.1, 923.0], [65.2, 928.0], [65.3, 932.0], [65.4, 933.0], [65.5, 940.0], [65.6, 940.0], [65.7, 944.0], [65.8, 945.0], [65.9, 946.0], [66.0, 948.0], [66.1, 949.0], [66.2, 949.0], [66.3, 956.0], [66.4, 958.0], [66.5, 963.0], [66.6, 965.0], [66.7, 965.0], [66.8, 967.0], [66.9, 970.0], [67.0, 970.0], [67.1, 976.0], [67.2, 978.0], [67.3, 978.0], [67.4, 984.0], [67.5, 993.0], [67.6, 996.0], [67.7, 1001.0], [67.8, 1001.0], [67.9, 1002.0], [68.0, 1002.0], [68.1, 1004.0], [68.2, 1004.0], [68.3, 1004.0], [68.4, 1005.0], [68.5, 1005.0], [68.6, 1008.0], [68.7, 1009.0], [68.8, 1010.0], [68.9, 1010.0], [69.0, 1014.0], [69.1, 1015.0], [69.2, 1017.0], [69.3, 1018.0], [69.4, 1021.0], [69.5, 1025.0], [69.6, 1025.0], [69.7, 1027.0], [69.8, 1033.0], [69.9, 1035.0], [70.0, 1035.0], [70.1, 1036.0], [70.2, 1038.0], [70.3, 1038.0], [70.4, 1041.0], [70.5, 1043.0], [70.6, 1046.0], [70.7, 1051.0], [70.8, 1052.0], [70.9, 1054.0], [71.0, 1054.0], [71.1, 1056.0], [71.2, 1056.0], [71.3, 1061.0], [71.4, 1061.0], [71.5, 1075.0], [71.6, 1075.0], [71.7, 1078.0], [71.8, 1080.0], [71.9, 1083.0], [72.0, 1084.0], [72.1, 1087.0], [72.2, 1088.0], [72.3, 1088.0], [72.4, 1092.0], [72.5, 1103.0], [72.6, 1104.0], [72.7, 1104.0], [72.8, 1109.0], [72.9, 1109.0], [73.0, 1113.0], [73.1, 1116.0], [73.2, 1123.0], [73.3, 1126.0], [73.4, 1126.0], [73.5, 1131.0], [73.6, 1132.0], [73.7, 1138.0], [73.8, 1140.0], [73.9, 1143.0], [74.0, 1144.0], [74.1, 1148.0], [74.2, 1154.0], [74.3, 1157.0], [74.4, 1160.0], [74.5, 1160.0], [74.6, 1161.0], [74.7, 1164.0], [74.8, 1167.0], [74.9, 1168.0], [75.0, 1173.0], [75.1, 1174.0], [75.2, 1174.0], [75.3, 1177.0], [75.4, 1178.0], [75.5, 1182.0], [75.6, 1182.0], [75.7, 1183.0], [75.8, 1189.0], [75.9, 1192.0], [76.0, 1199.0], [76.1, 1201.0], [76.2, 1201.0], [76.3, 1202.0], [76.4, 1202.0], [76.5, 1202.0], [76.6, 1203.0], [76.7, 1203.0], [76.8, 1204.0], [76.9, 1206.0], [77.0, 1212.0], [77.1, 1212.0], [77.2, 1214.0], [77.3, 1216.0], [77.4, 1221.0], [77.5, 1222.0], [77.6, 1222.0], [77.7, 1224.0], [77.8, 1224.0], [77.9, 1227.0], [78.0, 1234.0], [78.1, 1235.0], [78.2, 1238.0], [78.3, 1238.0], [78.4, 1238.0], [78.5, 1240.0], [78.6, 1244.0], [78.7, 1247.0], [78.8, 1247.0], [78.9, 1247.0], [79.0, 1253.0], [79.1, 1253.0], [79.2, 1256.0], [79.3, 1261.0], [79.4, 1265.0], [79.5, 1272.0], [79.6, 1274.0], [79.7, 1275.0], [79.8, 1280.0], [79.9, 1282.0], [80.0, 1282.0], [80.1, 1282.0], [80.2, 1284.0], [80.3, 1288.0], [80.4, 1288.0], [80.5, 1289.0], [80.6, 1290.0], [80.7, 1291.0], [80.8, 1296.0], [80.9, 1296.0], [81.0, 1297.0], [81.1, 1299.0], [81.2, 1299.0], [81.3, 1300.0], [81.4, 1301.0], [81.5, 1306.0], [81.6, 1306.0], [81.7, 1309.0], [81.8, 1315.0], [81.9, 1316.0], [82.0, 1317.0], [82.1, 1317.0], [82.2, 1328.0], [82.3, 1328.0], [82.4, 1330.0], [82.5, 1332.0], [82.6, 1333.0], [82.7, 1338.0], [82.8, 1338.0], [82.9, 1342.0], [83.0, 1342.0], [83.1, 1345.0], [83.2, 1348.0], [83.3, 1354.0], [83.4, 1354.0], [83.5, 1360.0], [83.6, 1361.0], [83.7, 1364.0], [83.8, 1377.0], [83.9, 1381.0], [84.0, 1384.0], [84.1, 1387.0], [84.2, 1388.0], [84.3, 1394.0], [84.4, 1397.0], [84.5, 1397.0], [84.6, 1397.0], [84.7, 1397.0], [84.8, 1397.0], [84.9, 1412.0], [85.0, 1415.0], [85.1, 1426.0], [85.2, 1434.0], [85.3, 1434.0], [85.4, 1438.0], [85.5, 1438.0], [85.6, 1438.0], [85.7, 1449.0], [85.8, 1456.0], [85.9, 1457.0], [86.0, 1457.0], [86.1, 1461.0], [86.2, 1465.0], [86.3, 1470.0], [86.4, 1476.0], [86.5, 1478.0], [86.6, 1481.0], [86.7, 1481.0], [86.8, 1483.0], [86.9, 1483.0], [87.0, 1488.0], [87.1, 1494.0], [87.2, 1498.0], [87.3, 1499.0], [87.4, 1500.0], [87.5, 1503.0], [87.6, 1504.0], [87.7, 1509.0], [87.8, 1509.0], [87.9, 1514.0], [88.0, 1516.0], [88.1, 1517.0], [88.2, 1520.0], [88.3, 1529.0], [88.4, 1541.0], [88.5, 1544.0], [88.6, 1550.0], [88.7, 1553.0], [88.8, 1559.0], [88.9, 1559.0], [89.0, 1571.0], [89.1, 1572.0], [89.2, 1581.0], [89.3, 1594.0], [89.4, 1601.0], [89.5, 1619.0], [89.6, 1621.0], [89.7, 1627.0], [89.8, 1627.0], [89.9, 1633.0], [90.0, 1633.0], [90.1, 1633.0], [90.2, 1634.0], [90.3, 1656.0], [90.4, 1665.0], [90.5, 1668.0], [90.6, 1673.0], [90.7, 1683.0], [90.8, 1684.0], [90.9, 1685.0], [91.0, 1694.0], [91.1, 1698.0], [91.2, 1698.0], [91.3, 1701.0], [91.4, 1701.0], [91.5, 1712.0], [91.6, 1712.0], [91.7, 1718.0], [91.8, 1720.0], [91.9, 1721.0], [92.0, 1736.0], [92.1, 1740.0], [92.2, 1747.0], [92.3, 1747.0], [92.4, 1749.0], [92.5, 1749.0], [92.6, 1751.0], [92.7, 1753.0], [92.8, 1760.0], [92.9, 1761.0], [93.0, 1765.0], [93.1, 1780.0], [93.2, 1811.0], [93.3, 1845.0], [93.4, 1845.0], [93.5, 1852.0], [93.6, 1854.0], [93.7, 1860.0], [93.8, 1871.0], [93.9, 1884.0], [94.0, 1910.0], [94.1, 1920.0], [94.2, 1935.0], [94.3, 1946.0], [94.4, 1950.0], [94.5, 1950.0], [94.6, 1984.0], [94.7, 1994.0], [94.8, 1998.0], [94.9, 2016.0], [95.0, 2016.0], [95.1, 2017.0], [95.2, 2022.0], [95.3, 2026.0], [95.4, 2045.0], [95.5, 2050.0], [95.6, 2050.0], [95.7, 2068.0], [95.8, 2078.0], [95.9, 2091.0], [96.0, 2123.0], [96.1, 2153.0], [96.2, 2170.0], [96.3, 2176.0], [96.4, 2180.0], [96.5, 2183.0], [96.6, 2194.0], [96.7, 2194.0], [96.8, 2203.0], [96.9, 2237.0], [97.0, 2257.0], [97.1, 2260.0], [97.2, 2269.0], [97.3, 2274.0], [97.4, 2303.0], [97.5, 2314.0], [97.6, 2365.0], [97.7, 2390.0], [97.8, 2390.0], [97.9, 2462.0], [98.0, 2602.0], [98.1, 2667.0], [98.2, 2674.0], [98.3, 2792.0], [98.4, 2947.0], [98.5, 3217.0], [98.6, 3298.0], [98.7, 3569.0], [98.8, 3581.0], [98.9, 3581.0], [99.0, 3581.0], [99.1, 3793.0], [99.2, 4496.0], [99.3, 5063.0], [99.4, 5088.0], [99.5, 5194.0], [99.6, 5344.0], [99.7, 6389.0], [99.8, 7915.0], [99.9, 9166.0], [100.0, 9166.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
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
        data: {"result": {"minY": 1.0, "minX": 300.0, "maxY": 301.0, "series": [{"data": [[9100.0, 1.0], [600.0, 67.0], [700.0, 52.0], [800.0, 48.0], [900.0, 32.0], [1000.0, 43.0], [1100.0, 33.0], [1200.0, 47.0], [1300.0, 33.0], [1400.0, 23.0], [1500.0, 18.0], [1600.0, 17.0], [1700.0, 18.0], [1800.0, 7.0], [1900.0, 8.0], [2000.0, 10.0], [2100.0, 7.0], [2200.0, 6.0], [2300.0, 4.0], [2400.0, 1.0], [2600.0, 3.0], [2700.0, 1.0], [2900.0, 1.0], [3200.0, 2.0], [3500.0, 3.0], [3700.0, 1.0], [4400.0, 1.0], [300.0, 2.0], [5000.0, 2.0], [5100.0, 1.0], [5300.0, 1.0], [6300.0, 1.0], [400.0, 114.0], [7900.0, 1.0], [500.0, 301.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 9100.0, "title": "Response Time Distribution"}},
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
        data: {"result": {"minY": 114.0, "minX": 0.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 677.0, "series": [{"data": [[0.0, 119.0]], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [[1.0, 677.0]], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [[2.0, 114.0]], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 2.0, "title": "Synthetic Response Times Distribution"}},
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
        data: {"result": {"minY": 188.86836935167, "minX": 1.79243016E12, "maxY": 210.7206982543642, "series": [{"data": [[1.79243016E12, 210.7206982543642], [1.79243022E12, 188.86836935167]], "isOverall": false, "label": "Virtual Users", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79243022E12, "title": "Active Threads Over Time"}},
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
        data: {"result": {"minY": 356.0, "minX": 1.0, "maxY": 2404.4, "series": [{"data": [[2.0, 610.0], [3.0, 641.0], [4.0, 1488.0], [5.0, 469.0], [6.0, 513.0], [7.0, 433.0], [8.0, 1457.0], [9.0, 439.0], [10.0, 1984.0], [11.0, 483.0], [12.0, 504.0], [13.0, 571.0], [14.0, 537.0], [15.0, 566.0], [16.0, 474.0], [17.0, 451.0], [18.0, 609.0], [19.0, 477.0], [20.0, 433.0], [21.0, 460.0], [22.0, 445.0], [23.0, 480.0], [24.0, 394.0], [25.0, 1668.0], [26.0, 570.0], [28.0, 552.5], [29.0, 553.0], [30.0, 567.0], [31.0, 514.0], [32.0, 807.0], [35.0, 1132.0], [34.0, 521.0], [36.0, 600.0], [39.0, 503.0], [38.0, 755.5], [41.0, 1884.0], [40.0, 455.0], [43.0, 558.0], [42.0, 1950.0], [45.0, 590.0], [44.0, 1306.0], [47.0, 543.0], [46.0, 597.0], [49.0, 923.0], [48.0, 601.0], [51.0, 501.0], [50.0, 1247.0], [53.0, 518.0], [52.0, 594.0], [55.0, 1330.0], [54.0, 491.0], [57.0, 1161.0], [56.0, 1092.0], [59.0, 1291.0], [58.0, 570.0], [61.0, 574.0], [60.0, 515.0], [63.0, 553.0], [62.0, 588.0], [67.0, 888.0], [66.0, 491.0], [65.0, 576.0], [64.0, 580.0], [71.0, 499.0], [70.0, 461.0], [69.0, 502.0], [68.0, 807.0], [75.0, 1470.0], [74.0, 572.0], [73.0, 574.0], [72.0, 538.0], [77.0, 1122.4], [78.0, 869.5], [79.0, 928.6666666666666], [76.0, 526.0], [80.0, 1202.3333333333333], [81.0, 889.25], [82.0, 1136.5], [83.0, 1461.0], [84.0, 613.0], [86.0, 672.5], [87.0, 522.0], [85.0, 514.0], [88.0, 661.3333333333334], [91.0, 587.0], [90.0, 525.0], [89.0, 530.0], [95.0, 621.5], [94.0, 543.0], [93.0, 587.0], [92.0, 534.0], [96.0, 686.3333333333334], [99.0, 495.0], [98.0, 409.0], [97.0, 457.0], [102.0, 654.5], [103.0, 666.0], [101.0, 516.0], [100.0, 507.0], [105.0, 1133.5], [107.0, 1335.0], [106.0, 519.0], [104.0, 470.0], [108.0, 661.5], [110.0, 1353.2], [111.0, 1291.0], [109.0, 1465.0], [115.0, 631.0], [114.0, 562.0], [113.0, 356.0], [112.0, 564.0], [116.0, 680.5], [117.0, 793.5], [118.0, 840.3333333333334], [119.0, 647.0], [120.0, 1586.4], [121.0, 1249.75], [122.0, 906.0], [123.0, 1132.0], [124.0, 1483.5], [126.0, 1146.3333333333333], [127.0, 517.0], [129.0, 1385.0], [130.0, 979.5], [131.0, 1163.6666666666667], [134.0, 741.0], [135.0, 1133.5], [133.0, 569.0], [132.0, 526.0], [128.0, 575.0], [136.0, 725.5], [139.0, 1342.0], [140.0, 1957.5], [141.0, 753.25], [142.0, 710.5], [143.0, 1238.0], [138.0, 611.5], [144.0, 776.5], [148.0, 723.3333333333334], [151.0, 665.0], [150.0, 551.0], [149.0, 590.0], [147.0, 567.0], [146.0, 530.0], [145.0, 598.0], [152.0, 1236.3333333333333], [154.0, 1374.0], [155.0, 1790.2], [158.0, 938.3333333333334], [159.0, 1301.0], [157.0, 437.0], [156.0, 459.0], [153.0, 521.0], [161.0, 1161.7142857142856], [163.0, 1125.5], [164.0, 838.5], [167.0, 660.0], [166.0, 477.0], [165.0, 810.0], [162.0, 503.0], [160.0, 496.0], [169.0, 855.3333333333334], [170.0, 889.0], [174.0, 535.0], [173.0, 539.5], [171.0, 587.0], [168.0, 624.0], [176.0, 1034.0], [178.0, 1324.5], [180.0, 674.0], [182.0, 1552.0], [183.0, 1018.3333333333334], [181.0, 554.0], [179.0, 567.0], [177.0, 605.0], [184.0, 1203.6666666666667], [185.0, 675.5], [186.0, 1678.5], [189.0, 2404.4], [191.0, 517.0], [190.0, 556.0], [188.0, 628.0], [187.0, 511.0], [192.0, 994.5], [195.0, 851.0], [196.0, 737.5], [199.0, 574.0], [198.0, 568.0], [197.0, 614.0], [194.0, 1001.0], [193.0, 580.0], [204.0, 703.0], [205.0, 1346.2], [206.0, 1049.3333333333333], [207.0, 614.0], [203.0, 595.0], [202.0, 591.0], [201.0, 474.0], [200.0, 490.0], [208.0, 1122.75], [209.0, 807.0], [215.0, 585.0], [214.0, 464.0], [213.0, 595.0], [212.0, 566.0], [211.0, 468.0], [210.0, 1299.0], [216.0, 1136.25], [217.0, 1169.8333333333333], [218.0, 2007.6666666666665], [219.0, 1167.0], [223.0, 571.0], [222.0, 569.0], [221.0, 978.0], [220.0, 1685.0], [224.0, 749.0], [225.0, 782.5], [226.0, 1476.3333333333333], [229.0, 1000.5], [231.0, 1476.5], [230.0, 524.0], [228.0, 542.0], [227.0, 580.0], [234.0, 1105.6666666666667], [237.0, 1098.5], [238.0, 903.75], [239.0, 809.6666666666666], [236.0, 504.0], [232.0, 559.0], [240.0, 814.0], [241.0, 624.0], [242.0, 843.3333333333334], [243.0, 1450.25], [245.0, 835.25], [246.0, 738.0], [247.0, 1163.75], [248.0, 946.8], [249.0, 980.75], [250.0, 927.237791932059], [1.0, 599.0]], "isOverall": false, "label": "API Request", "isController": false}, {"data": [[198.49780219780226, 936.7153846153832]], "isOverall": false, "label": "API Request-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 250.0, "title": "Time VS Threads"}},
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
        data : {"result": {"minY": 835.4166666666666, "minX": 1.79243016E12, "maxY": 9997.266666666666, "series": [{"data": [[1.79243016E12, 7875.816666666667], [1.79243022E12, 9997.266666666666]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.79243016E12, 835.4166666666666], [1.79243022E12, 1060.4166666666667]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79243022E12, "title": "Bytes Throughput Over Time"}},
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
        data: {"result": {"minY": 744.5245579567786, "minX": 1.79243016E12, "maxY": 1180.6683291770578, "series": [{"data": [[1.79243016E12, 1180.6683291770578], [1.79243022E12, 744.5245579567786]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79243022E12, "title": "Response Time Over Time"}},
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
        data: {"result": {"minY": 744.5108055009827, "minX": 1.79243016E12, "maxY": 1180.6034912718198, "series": [{"data": [[1.79243016E12, 1180.6034912718198], [1.79243022E12, 744.5108055009827]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79243022E12, "title": "Latencies Over Time"}},
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
        data: {"result": {"minY": 0.0, "minX": 1.79243016E12, "maxY": 228.01246882793012, "series": [{"data": [[1.79243016E12, 228.01246882793012], [1.79243022E12, 0.0]], "isOverall": false, "label": "API Request", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79243022E12, "title": "Connect Time Over Time"}},
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
        data: {"result": {"minY": 356.0, "minX": 1.79243016E12, "maxY": 9166.0, "series": [{"data": [[1.79243016E12, 6389.0], [1.79243022E12, 9166.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.79243016E12, 402.0], [1.79243022E12, 356.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.79243016E12, 2016.8], [1.79243022E12, 1288.0]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.79243016E12, 5087.5], [1.79243022E12, 2021.3999999999999]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.79243016E12, 996.0], [1.79243022E12, 571.0]], "isOverall": false, "label": "Median", "isController": false}, {"data": [[1.79243016E12, 2359.8999999999987], [1.79243022E12, 1517.5]], "isOverall": false, "label": "95th percentile", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79243022E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
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
    data: {"result": {"minY": 480.0, "minX": 2.0, "maxY": 1354.0, "series": [{"data": [[8.0, 562.5], [2.0, 608.5], [37.0, 1354.0], [9.0, 566.0], [10.0, 629.5], [11.0, 618.0], [46.0, 1276.0], [49.0, 1202.0], [12.0, 571.0], [13.0, 593.0], [54.0, 1174.0], [14.0, 578.0], [15.0, 568.5], [4.0, 625.5], [16.0, 563.0], [17.0, 565.0], [73.0, 1036.0], [18.0, 589.5], [19.0, 480.0], [20.0, 555.5], [21.0, 561.5], [6.0, 568.0], [7.0, 570.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 73.0, "title": "Response Time Vs Request"}},
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
    data: {"result": {"minY": 480.0, "minX": 2.0, "maxY": 1354.0, "series": [{"data": [[8.0, 562.5], [2.0, 608.5], [37.0, 1354.0], [9.0, 566.0], [10.0, 629.5], [11.0, 618.0], [46.0, 1276.0], [49.0, 1202.0], [12.0, 571.0], [13.0, 593.0], [54.0, 1174.0], [14.0, 578.0], [15.0, 568.5], [4.0, 625.5], [16.0, 563.0], [17.0, 565.0], [73.0, 1036.0], [18.0, 589.5], [19.0, 480.0], [20.0, 555.5], [21.0, 561.5], [6.0, 568.0], [7.0, 570.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 73.0, "title": "Latencies Vs Request"}},
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
        data: {"result": {"minY": 6.75, "minX": 1.79243016E12, "maxY": 8.416666666666666, "series": [{"data": [[1.79243016E12, 6.75], [1.79243022E12, 8.416666666666666]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79243022E12, "title": "Hits Per Second"}},
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
        data: {"result": {"minY": 6.683333333333334, "minX": 1.79243016E12, "maxY": 8.483333333333333, "series": [{"data": [[1.79243016E12, 6.683333333333334], [1.79243022E12, 8.483333333333333]], "isOverall": false, "label": "200", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79243022E12, "title": "Codes Per Second"}},
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
        data: {"result": {"minY": 6.683333333333334, "minX": 1.79243016E12, "maxY": 8.483333333333333, "series": [{"data": [[1.79243016E12, 6.683333333333334], [1.79243022E12, 8.483333333333333]], "isOverall": false, "label": "API Request-success", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79243022E12, "title": "Transactions Per Second"}},
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
        data: {"result": {"minY": 6.683333333333334, "minX": 1.79243016E12, "maxY": 8.483333333333333, "series": [{"data": [[1.79243016E12, 6.683333333333334], [1.79243022E12, 8.483333333333333]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79243022E12, "title": "Total Transactions Per Second"}},
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

