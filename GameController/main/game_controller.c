#include <stdio.h>
#include <string.h>
#include <driver/gpio.h>

#include <driver/uart.h>
#include "driver/i2c.h"

#include <freertos/FreeRTOS.h>
#include <freertos/task.h>


#define UPDATE_CONTROLLER_DELAY 100                             // ms

#define UART_NUM UART_NUM_0                                     // UART 0 hard connected to USB-UART bridge
#define UART_BUF_SIZE 1024
#define UART_BAUD_RATE 9600

#define I2C_MASTER_NUM      I2C_NUM_0                           
#define I2C_MASTER_SDA_IO   21                                  
#define I2C_MASTER_SCL_IO   22                                  
#define I2C_MASTER_FREQ_HZ  100000                              
#define I2C_MASTER_TX_BUF_DISABLE 0
#define I2C_MASTER_RX_BUF_DISABLE 0

#define MPU6500_I2C_ADDRESS 0x68
#define MPU6500_START_REG 0x43
#define MPU6500_BYTES_TO_READ 6

static void init_uart();
static void init_i2c_master();
static void wake_up_mpu6500();
static void read_mpu6500_data(uint8_t *mpu6500_data);
static void update_controller_pos(void *pvParameters);


static void init_uart() {
    uart_config_t uart_config = {
        .baud_rate = UART_BAUD_RATE,          
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };
    uart_param_config(UART_NUM, &uart_config);
    uart_driver_install(UART_NUM, UART_BUF_SIZE * 2, 0, 0, NULL, 0);
    printf("\n");
}

static void init_i2c_master() {
    esp_err_t err;
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ
    };
    err = i2c_param_config(I2C_MASTER_NUM, &conf);
    if (err == ESP_OK) {
        err = i2c_driver_install(I2C_MASTER_NUM, conf.mode, I2C_MASTER_RX_BUF_DISABLE, I2C_MASTER_TX_BUF_DISABLE, 0);
        if (err != ESP_OK) printf("(E) i2c driver install: %s\n", esp_err_to_name(err));
    }
    else printf("(E) i2c param config: %s\n", esp_err_to_name(err));
}

static void wake_up_mpu6500() {
    uint8_t wake_cmd[2] = {0x6B, 0x00};  // PWR_MGMT_1 = 0
    esp_err_t err = i2c_master_write_to_device(I2C_MASTER_NUM, MPU6500_I2C_ADDRESS, wake_cmd, 2, pdMS_TO_TICKS(100));
    if (err != ESP_OK) printf("(E) i2c wake mpu6500: %s\n", esp_err_to_name(err));
}

static void update_controller_pos(void *pvParameters) {
    for (;;) {
        uint8_t mpu6500_data[MPU6500_BYTES_TO_READ];
        read_mpu6500_data(mpu6500_data);
        uart_write_bytes(UART_NUM, mpu6500_data, MPU6500_BYTES_TO_READ);
        vTaskDelay(pdMS_TO_TICKS(UPDATE_CONTROLLER_DELAY));                        
    }
}

static void read_mpu6500_data(uint8_t *mpu6500_data) {
    esp_err_t err;
    uint8_t reg = MPU6500_START_REG;
    err = i2c_master_write_to_device(I2C_MASTER_NUM, MPU6500_I2C_ADDRESS, &reg, 1, pdMS_TO_TICKS(1000));
    if (err != ESP_OK) printf("(E) i2c write mpu6500: %s/n", esp_err_to_name(err));
    
    err = i2c_master_read_from_device(I2C_MASTER_NUM, MPU6500_I2C_ADDRESS, mpu6500_data, MPU6500_BYTES_TO_READ, pdMS_TO_TICKS(1000));
    if (err != ESP_OK) printf("(E) i2c read mpu6500: %s/n", esp_err_to_name(err));
}

void app_main(void) {
    init_uart();
    init_i2c_master();
    wake_up_mpu6500();
    xTaskCreate(update_controller_pos, "update_controller_pos", 4096, NULL, 5, NULL);
}
