#include <stdio.h>
#include <string.h>
#include <driver/uart.h>
#include <driver/gpio.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#define UART_NUM UART_NUM_0                                     // UART 0 hard connected to USB-UART bridge
#define UART_BUF_SIZE 1024

static void init_uart();
static void send_controller_pos();
static void update_controller_pos(void *pvParameters);

void init_uart() {
    uart_config_t uart_config = {
        .baud_rate = 9600,          
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };
    uart_param_config(UART_NUM, &uart_config);
    uart_driver_install(UART_NUM, UART_BUF_SIZE * 2, 0, 0, NULL, 0);
}

void update_controller_pos(void *pvParameters) {
    for (;;) {
        // read sensor
        send_controller_pos();
        vTaskDelay(pdMS_TO_TICKS(16));                          // Game refreshes with 60 hz
    }
}

void send_controller_pos() {
    // The string to send
    const char *test_str = "Hello COM5 from ESP32!\n";
    uart_write_bytes(UART_NUM, test_str, strlen(test_str));
    vTaskDelay(pdMS_TO_TICKS(1000)); 
}

void app_main(void) {
    init_uart();
    xTaskCreate(update_controller_pos, "update_controller_pos", 2048, NULL, 5, NULL);
}
