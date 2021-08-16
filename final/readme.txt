檔案說明:

edge資料夾內為實作AR用的, 需放server的container中並執行
    其中app.py會接收request並以AR的三個步驟(detect, project, render)跑同一張圖數次, 回傳所花的運算時間
    models內的spider.obj為要渲染的物件
    reference內的model.jpg為要detect的物件形狀
    AR_task.jpg為用來跑AR的同一張圖
    AR_local是用來測試AR功能的, 僅會在本地端跑 並會抓webcam作為影像源
    client.py是用來測試edge server中app.py執行的功能的, 會發request到指定ip port並輸出response

experiment資料夾內為實驗主要執行的.py
    其中simulation.py是跑SP2純模擬圖的 以及optimal的圖
    implementation.py是跑SP2實作圖的 (差別在offloading的部分會發request到container執行AR)
    RL.py是跑SP1圖的
    train_x.pickle與train_y.pickle是我拿來跑DNN對不同layer/neuron數使用的事先準備RL的experiences data
    CPUload是我測試不同cpu quota對單位task的執行時間的圖
    train.dat為所使用的youtube traffic資料庫

實作環境:GCP 8CPU VM ubuntu 20.04, 開完VM需自己裝docker以及python會用到的套件

常用指令:
stress-ng -c 0 -l 50 #壓力指令
sudo apt-get install docker.io #安裝docker
sudo docker images #check current images list
sudo docker rmi image_id
sudo docker ps -a #check current container list
sudo docker stop container_id 
sudo docker rm container_id
sudo docker build -t appname . #在build container時需要把所有環境放在同個目錄下 詳情見reference. edge資料夾中有我當時用的環境
sudo docker run -d -p 80:4000 appname 
sudo docker run -d -p 80:4000 --cpu-quota=500000 test2 #把container的port 80接到 port 4000, 並限制CPU quota=500000 單位未知, 對應到算力的大小需要自己試

reference:
https://blog.gtwang.org/virtualization/docker-basic-tutorial/2/