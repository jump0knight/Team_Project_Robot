#include <Arduino.h>
#include <esp_now.h>
#include <WiFi.h>

// 目标设备的 MAC 地址
uint8_t broadcastAddress[] = {0xf0, 0xf5, 0xbd, 0x19, 0xa2, 0x30};  
int mode = 0; 
byte receive_data[8];

// 发送的数据结构
typedef struct struct_message
{
  byte header1;      // 帧头第一字节 0xFF
  byte header2;      // 帧头第二字节 0xAA
  byte mode;         // 模式选择位
  byte data[8];      // 数据部分，最大 8 字节
  byte footer1;      // 帧尾第一字节 0xBF
  byte footer2;      // 帧尾第二字节 0xC0
} struct_message;

struct_message myData;
esp_now_peer_info_t peerInfo;
struct_message receivedData;  // 在全局范围内定义接收数据的结构体

// 发送数据回调函数
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status)
{
    Serial.print("Last Packet Send Status: ");
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

// 接收数据回调函数
void OnDataReceived(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
    // 将接收到的数据复制到结构体中
    memcpy(&receivedData, data, sizeof(receivedData));

    // 校验帧头和帧尾是否正确
    if (receivedData.header1 == 0xFF && receivedData.header2 == 0xAA && receivedData.footer1 == 0xBF && receivedData.footer2 == 0xC0) {
        // 打印接收到的数据
        mode = receivedData.mode;
        Serial.println("Data received:");

        // 重新打包数据并通过串口发送
        for (int i = 0; i < sizeof(receivedData.data); i++) {
            receive_data[i] = receivedData.data[i];
        }
        
        // 重新打包数据帧头、模式、数据和帧尾
        struct_message sendData;
        sendData.header1 = 0xFF;
        sendData.header2 = 0xAA;
        sendData.mode = receivedData.mode;  // 使用接收到的模式
        memcpy(sendData.data, receivedData.data, sizeof(receivedData.data));  // 使用接收到的数据
        sendData.footer1 = 0xBF;
        sendData.footer2 = 0xC0;

        // 将重新打包的数据通过串口1发送出去（TX = GPIO43, RX = GPIO44）
        Serial1.write((uint8_t*)&sendData, sizeof(sendData));
        Serial.println("Sent data via Serial1:");

        // 打印发送的数据
        for (int i = 0; i < sizeof(sendData.data); i++) {
            Serial.printf("Sending data %d: 0x%02X\n", i + 1, sendData.data[i]);
        }
    }
}

void setup()
{
    Serial.begin(115200);  // 使用默认串口与PC通信
    // 使用串口1，TX = GPIO43，RX = GPIO44
    Serial1.begin(115200, SERIAL_8N1, 43, 44);  

    WiFi.mode(WIFI_STA);  // 设置为 Station 模式

    if (esp_now_init() != ESP_OK)
    {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    esp_now_register_send_cb(OnDataSent);  // 注册发送数据的回调函数
    esp_now_register_recv_cb(OnDataReceived);  // 注册接收数据的回调函数

    // 配置目标设备的 MAC 地址
    memcpy(peerInfo.peer_addr, broadcastAddress, 6);
    peerInfo.channel = 0;  // 使用当前打开的通道
    peerInfo.encrypt = false;  // 不使用加密

    // 添加 peer
    if (esp_now_add_peer(&peerInfo) != ESP_OK)
    {
        Serial.println("Failed to add peer");
        return;
    }
}

// 数据处理函数
void Data_process(struct_message *myData, int mode_ch, byte *data, int dataLength) {
    myData->header1 = 0xFF;
    myData->header2 = 0xAA;
    myData->footer1 = 0xBF;
    myData->footer2 = 0xC0;

    myData->mode = mode_ch;

    // 填充数据部分
    for (int i = 0; i < dataLength && i < sizeof(myData->data); i++) {
        myData->data[i] = data[i];
    }
}

byte Data[] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06};

void loop()
{
    // 调用数据处理函数，传递结构体、模式选择位和数据
    Data_process(&myData, 0x01, Data, sizeof(Data));

    // 发送数据
    esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *)&myData, sizeof(myData));  // 发送数据

    if (result == ESP_OK)
    {
        Serial.println("Sent with success");
    }
    else
    {
        Serial.println("Error sending the data");
    }
}
