/*
 *  Copyright (C) 2022  Skip Hansen
 * 
 *  This program is free software; you can redistribute it and/or modify it
 *  under the terms and conditions of the GNU General Public License,
 *  version 2, as published by the Free Software Foundation.
 *
 *  This program is distributed in the hope it will be useful, but WITHOUT
 *  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 *  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 *  more details.
 *
 *  You should have received a copy of the GNU General Public License along
 *  with this program; if not, write to the Free Software Foundation, Inc.,
 *  51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.
 *
 *  Much of this code derived from Raspberry Pi Pico demos (https://github.com/raspberrypi/pico-examples)
 *  with the following license:
 *
 * Copyright (c) 2020 Raspberry Pi (Trading) Ltd.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */
#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/bootrom.h"
#include "hardware/gpio.h"
#include "hardware/sync.h"
#include "hardware/structs/ioqspi.h"

bool __no_inline_not_in_flash_func(get_bootsel_button)() 
{
   const uint CS_PIN_INDEX = 1;

   // Must disable interrupts, as interrupt handlers may be in flash, and we
   // are about to temporarily disable flash access!
   uint32_t flags = save_and_disable_interrupts();

   // Set chip select to Hi-Z
   hw_write_masked(&ioqspi_hw->io[CS_PIN_INDEX].ctrl,
                   GPIO_OVERRIDE_LOW << IO_QSPI_GPIO_QSPI_SS_CTRL_OEOVER_LSB,
                   IO_QSPI_GPIO_QSPI_SS_CTRL_OEOVER_BITS);

   // Note we can't call into any sleep functions in flash right now
   for(volatile int i = 0; i < 1000; ++i);

   // The HI GPIO registers in SIO can observe and control the 6 QSPI pins.
   // Note the button pulls the pin *low* when pressed.
   bool button_state = !(sio_hw->gpio_hi_in & (1u << CS_PIN_INDEX));

   // Need to restore the state of chip select, else we are going to have a
   // bad time when we return to code in flash!
   hw_write_masked(&ioqspi_hw->io[CS_PIN_INDEX].ctrl,
                   GPIO_OVERRIDE_NORMAL << IO_QSPI_GPIO_QSPI_SS_CTRL_OEOVER_LSB,
                   IO_QSPI_GPIO_QSPI_SS_CTRL_OEOVER_BITS);

   restore_interrupts(flags);

   return button_state;
}

int main() 
{
   const uint LED_PIN = PICO_DEFAULT_LED_PIN;
   int Loops = 0;

   gpio_init(LED_PIN);
   gpio_set_dir(LED_PIN, GPIO_OUT);
   stdio_init_all();

   while(true) {
      printf("Hello world %d\n",Loops++);
      gpio_put(LED_PIN,1);
      sleep_ms(250);
      gpio_put(LED_PIN, 0);
      sleep_ms(250);
      if(get_bootsel_button()) {
      // Back to boot mode
         reset_usb_boot(0,0);
      }
   }
}

