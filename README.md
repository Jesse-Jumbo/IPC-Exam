# IPC-Exam
An offline version for 2021 entrance exam (2021)

[TOC]

概述
--

平行運算 (parallel computing) 是指許多行程（processes）得以同時進行的計算模式。透過將問題拆解成諸多不同的小問題，使得多個行程得以同時解決這些小問題，來加速程式的運行。舉例來說，矩陣相乘的運算就很適合使用平行運算來處理，因為中間的運算都是獨立的過程：

$$
\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}\begin{bmatrix}
e & f \\
g & h
\end{bmatrix} = \begin{bmatrix}
ae+bg & af+bh \\
ce+dg & cf+dh
\end{bmatrix} 
$$

影像處理的領域中也常常見到平行處理的應用。在影像處理的領域中，我們常常用一個較小的矩陣 —— kernel（或者稱做 mask）—— 與影像進行 **二維卷積2D convolution** (請參考 **\[相關資料\]** 章節) 處理。經由與不同的核進行 convolution，來完成影像的邊緣偵測或是使影像邊緣模糊化。

然而，大尺寸的影像在進行 2D convolution 時，需要花費大量的運算時間，造成效能瓶頸。因此，在這次考試中，希望 妳/你 能在給定的架構下，平行化處理影像的二維卷積。

考試要求
----

請在閱讀完文件後，依照其中軟體架構的說明建立系統。考生需：

1.  排除程式內部的錯誤，使得系統能正常運行
    
2.  成功建立系統後，透過參數的調整或是程式優化的技巧來加速運算。
    

成績採計方式
------

軟體說明
----

### 系統流程

考生可以對照圖（一）的架構，或圖（二）的 sequence diagram，逐步了解系統流程。

**圖 (ㄧ)** 系統架構圖

**圖 (二)** Sequence diagram

| 圖(一) 系統架構圖 | 圖(二) Sequence diagram |
| --- | --- |
| ![img](https://i.imgur.com/wTnDBaO.jpg) | ![圖二](https://i.imgur.com/7wX7zh2.jpg) |


1.  `Producer` 傳送開始訊號給 `System`

2.  `System` 回傳待處理的圖片路徑給 `Producer`，並同時開始計時

3.  `Producer` 發送任務給一至多個 `Consumer(s)`

4.  `Consumer` 各自完成任務後傳送結果給 `ResultCollector`

5.  `ResultCollector` 接收完所有子任務後將其統整，再傳送結束訊息給 `System`。`System` 結束計時。

6.  `System` 驗證答案正確性，回傳本次任務狀態給 `ResultCollector`
    

### 程式內部流程

在本次考試中，考生須要對系統中的三支程式進行改進與改正，包括 `Producer.py`、`Consumer.c` 以及 `ResultCollector.py`。三者分別對應到**圖 (一)**的 `Producer`,`Consumer` 和 `Result Collector`。本節將對這三支程式的細節與流程進行解說。

#### Producer

*   系統參數設定
    
    | 參數 | 說明 |
    | --- | --- |
    | `image_path` | 本次任務處理的圖片路徑 |
    | `socket_system_server` | `Producer` 與 `System` 連接的 socket port |
    | `socket_producer_consumer` | `Producer` 與 `Consumer` 連接的 socket port |
    | `num_to_split` | 分派的子任務數量 |
    
*   說明
    
    * `Producer` 會與 `System` 和 `Consumer` 進行連線，並分別以 **Request/Reply** 和 **Pull/Push** 的模式溝通 (模式說明請參閱 **\[相關資料\]** 章節)。
        
        `Producer` 與 `System`間以 **Request/Reply** 的模式連接，兩者綁定在系統參數 `socket_system_server` 所指定的 port。`Producer` 會從`System` 得到一組圖片路徑 `image_path`，作為本次處理的任務。
        
        另一方面， `Producer` 與 `Consumer` 則是以 **Pull/Push** 的模式連接，兩者綁定在系統參數中 `socket_producer_consumer` 所指定的 port。系統運行中，`Consumer` 會不斷地去 pull 由`Producer` push 的任務來進行處理。
        
        我們可以在 **圖 (三)** 的流程圖中了解 `Producer` 這支程式執行的邏輯：
        

| **圖 (三)** Producer 運行的流程圖 | 說明 |
| --- | --- |
| ![img](https://i.imgur.com/WDfSUUB.jpg) | 1. 生產者會先設定與消費者及伺服器之連線  <br>2. 送出開始訊號  <br>3. 等待伺服器端給予回覆，直至收到伺服器端回覆的圖片路徑  <br>4. 生產者讀取該位置的圖片，並根據系統參數設定檔中 `num_to_split` 來設定拆分的子任務的數量  <br>5. 傳送任務給消費者  <br>6. 傳送完成後，關閉開啟的 socket 埠 |

#### Consumer

*   系統參數設定
    
    | 參數 | 說明 |
    | --- | --- |
    | `socket_producer_consumer` | `Consumer` 與 `Producer` 連接的 socket port |
    | `socket_consumer_collector` | `Consumer` 與 `Collector` 連接的 socket port |
    | `num_of_consumers` | 指派系統使用的 `Consumer` 數量 |
    
*   說明
    
    *   `Consumer` 會與 `Producer` 和 `Collector` 進行連線，其模式可以比照 **圖 (一)** 所示，並以 **Pull/Push** 的模式溝通 (模式說明請參閱 **\[相關資料\]** 章節)。 此兩者綁定的 port 亦可在系統參數設定檔進行設定，分別是 `socket_producer_consumer` 與 `socket_consumer_collector` 這兩個參數。 另外，透過設定系統參數中的 `num_of_consumers` 可以指定系統執行 `Consumer` 的 process 數量。

        我們可以在 **圖 (四)** 的流程圖中了解 `Consumer` 這支程式執行的邏輯：
        

| 圖 (四) Consumer 運行的流程圖 | 說明 |
|---|---|
| ![img](https://i.imgur.com/ACNQC1j.jpg) | 1. 設定與生產者與結果收集器之連線設定  <br>2. 等待任務  <br>3. 當接收到任務後由 Worker 進行任務處理  <br>4. 將結果傳送到結果收集器  <br>5. 若無中斷則回到步驟二，等待接收新的任務  <br>6. 若被中斷則結束程式 |

#### ResultCollector

*   系統參數設定
    
    | 參數 | 說明 |
    | --- | --- |
    | `socket_system_server` | `Collector` 與 `System` 連接的 socket port |
    | `socket_consumer_collector` | `Collector` 與 `Consumer` 連接的 socket port |
    
*   說明
    
    *   `Collector` 會與 `System` 和 `Consumer` 進行連線，並分別以 **Request/Reply** 和 **Pull/Push** 的模式溝通 (模式說明請參閱 **\[相關資料\]** 章節)。

        `Collector` 與 `System`間以 **Request/Reply** 的模式連接，兩者綁定在系統參數 `socket_system_server` 所指定的 port。`Collector` 會從 `System` 得到該次任務處理完成的狀態。
        
        另一方面， `Collector` 與 `Consumer` 則是以 **Pull/Push** 的模式連接，兩者綁定在系統參數中 `socket_consumer_collector` 所指定的 port。系統運行中，`Collector` 會不斷地去接收 由`Consumer` 運算完成的子任務。
        
        我們可以在 **圖 (五)** 的流程圖中了解 `Collector` 這支程式執行的邏輯：
        

| 圖 (五) ResultCollector 運行的流程圖 | 說明 |
| --- | --- |
| ![img](https://i.imgur.com/HCB6NRT.jpg) | 1. 設定與消費者與伺服器之連線  <br>2. Pull 來自消費者的任務 <br>3. 若任務尚未收集完成，回到步驟二。否則繼續。 <br>4. 重組影像  <br>5. 儲存影像  <br>6. 顯示結果 |

### 資料結構

資料傳輸的 MessageBuffer 是以 JSON 的格式進行編碼，其中資訊如下表所示。

| KEY | 資料型態 | 說明 |
| --- | --- | --- |
| image | 2 dimentional array | |
| mask | 2 dimentional array | |
| point | 1 dimentional array | 左上角之座標 |
| total_buffer_num | Number | 子任務總數 |
| src_path | String | 圖片路徑 |

| 圖 (六) MessageBuffer 示意圖 |
| --- |
| ![](https://i.imgur.com/1zTuihu.png) |

檔案結構說明
------

```
.

+-- lib/
| +-- FFT/
+-- src/
| +-- System/
| | +-- test
| | +-- run
| +-- SystemParameter.json
| +-- Producer.py
| +-- Consumer.py
| +-- ResultCollector.py
| +-- makefile
+-- requirments.txt
+-- README.md
```

| 檔案/目錄 | 說明 |
| --- | --- |
| `src/SystemParameter.json` | 系統參數設定檔，其中定義了  <br>1. `userID`：請自行輸入准考證號碼  <br>2. `num_of_consumer`：指派系統開啟的 Consumer 數量  <br>3. `num_to_split`：分派的子任務數量  <br>4. `socket_producer_consumer`：Producer 與 Consumer 間溝通的 port <br>5. `socket_consumer_collector`：Consumer 與 Collector 間溝通的 port  <br>6. `socket_system_server`：Producer/Collector 與 System 溝通的 port |

執行方式
----

### 本地端

在 `src/` 底下執行

1. 系統建置測試
    *  在 Ubuntu 系統下，確認系統正常運作，執行 `System/test`
        ```    
        $ ./System/test
        ```
    * 非 Ubuntu 可執行 `test.py`

2. 指定圖片路徑測試    
    1.  設定環境參數 `image_path`，來指定圖片
        
        ```        
        // (SystemParameter.json)
        image\_path = [usr_defined_image_path]
        ```
        
    2.  執行 `System/run` (或於 `src/`執行 `python3 run.py`)
        
        ```
        $ ./System/run
        ```
        

### 伺服器端

請參照 考試須知文件 中程式系統的說明。

相關資料
----

### 二維卷積 (2D Convolution)

二維卷積是影像處理上常用的操作方式，透過使用不同的遮罩 (mask)，來對影像進行模糊、銳化、邊緣偵測等效果。一般來說，對於一個影像 II 和一個 大小為 $N. \cross M$ 的 mask $\omega$ ，convolution 的操作如下：

$
G(x,y) = \omega * I (x,y) = \Sigma_{dx=0}^{M} \Sigma_{dy=0}^{M} I(x+dx, y+dy)
$

其中 $G$ 是 convolution 完的圖片，透過 **方程式(2)** 可以求得 **G** 上的各點 。我們可以透過 **圖 (七)** 的範例了解 **方程式(2)**：

| 圖 (七) 2D convolution 範例 | 
| --- |
| ![](https://i.imgur.com/MR6GYJ1.gif) |

### Request/Reply Pattern

*   參考 [Client / Server — Learning 0MQ with examples (learning-0mq-with-pyzmq.readthedocs.io)](https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/client_server.html)

### Pull/Push Pattern

*   參考 [Push/Pull — Learning 0MQ with examples (learning-0mq-with-pyzmq.readthedocs.io)](https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pushpull.html)
