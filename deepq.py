    def algo_strategy(self, delta_power, power_realized):
        action_txt = ""
        sold_energy_battery = 0
        self.action_executed = False
        if delta_power < 0:
            if self.battery.SOC > self.battery.SOC_max:
                action_txt = 'sell'
                action = action_txt
                logging.info(action_txt)
                _, sold_energy_battery = self.battery.step(action_txt, delta_power*2, delta_t = 30)
                power_realized = power_realized - delta_power
            if self.battery.SOC >= self.battery.SOC_min and self.battery.SOC < self.battery.SOC_max:
                action_txt = 'sell'
                action = action_txt
                _, sold_energy_battery = self.battery.step(action, delta_power*2, delta_t = 30)
                power_realized = power_realized - delta_power
                logging.info(action_txt)
            if self.battery.SOC < self.battery.SOC_min:
                action_txt = 'stay'
                logging.info(action_txt)
                action = action_txt
        elif delta_power > 0:
            if self.battery.SOC > self.battery.SOC_max:
                action_txt = 'sell'
                logging.info(action_txt)
                _, sold_energy_battery = self.battery.step('sell', delta_power*2, delta_t = 30)
                power_realized = power_realized - delta_power
            if self.battery.SOC >= self.battery.SOC_min and self.battery.SOC < self.battery.SOC_max:
                action_txt = 'store'
                action = action_txt
                logging.info(action_txt)
                self.battery.step(action, delta_power*2, delta_t = 30)
                #power_realized = power_realized - delta_power
            if self.battery.SOC < self.battery.SOC_min:
                action_txt = 'store'
                logging.info(action_txt)
                action = action_txt
        else:
            if self.battery.SOC > self.battery.SOC_max:
                action_txt = 'sell'
                logging.info(action_txt)
                _, sold_energy_battery = self.battery.step('sell', delta_power*2, delta_t = 30)
                power_realized = power_realized - delta_power
            elif self.battery.SOC >= self.battery.SOC_min and self.battery.SOC < self.battery.SOC_max:
                action_txt = 'stay'
                action = action_txt
                logging.info(action_txt)
            else:
                action_txt = 'stay'
                logging.info(action_txt)
                action = action_txt
                
        self.power_sold = power_realized + np.abs(sold_energy_battery)
        logging.info(f'Sold energy from production: {power_realized}kW')
        logging.info(f'Sold energy from battery: {np.abs(sold_energy_battery)}kW')
        logging.info(f'Total sold energy: {self.power_sold}kW')
        return self.prv_action, action_txt, power_realized, sold_energy_battery

    def step(self, action):
        """
        Method taken from LCVEnv
        :param action:
        :return:
        """
        action = {k: v for k, v in zip(range(len(self.ACTIONS)), self.ACTIONS)}[action]
        if self.action_executed:
            self.reward = 1 if self.delta_pl > 0 else -1
        else:
            self.reward = 0
        self.prv_action = action
        return self.get_features(), self.reward, self.done

    def get_features(self):
        return np.array([np.round(float(self.power_current_realized), 2),
        	self.battery.storage_capacity,  # battery capacity
            self.battery.SOC,
            self.battery.SOC_min, # added on 31/7
            self.battery.SOC_max, # added on 31/7
            self.delta_power,
            self.power_current_realized_list[-1],
            self.power_current_realized_list[-2],
            self.power_current_realized_list[-3],
            np.mean(self.power_current_realized_list),
            np.std(self.power_current_realized_list), # added on 31/7
            self.price_spot,  # real time electricity price
            self.price_spot_list[-1],  # last 3 elect prices
            self.price_spot_list[-2],
            self.price_spot_list[-3],
            np.mean(self.price_spot_list),
            np.std(self.price_spot_list), # added on 31/7
            self.timestamp.month,
            self.timestamp.weekday(),
            self.timestamp.hour,] + list(self.power_current_intraday))
