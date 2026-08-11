/** @odoo-module **/

import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

// Создаем отдельный простой компонент контента для нашего поповера.
// Он будет отображать данные, переданные в него через props.
class AlarmPopoverContent extends Component {}
AlarmPopoverContent.template = "alarm_ukraine.AlarmPopoverContent";

class SystrayAlarm extends Component {
    setup() {
        this.state = useState({
            city: "Не визначено",
            alert: false,
            updated: "--:--",
        });

        this.orm = useService("orm");
        this.popover = useService("popover");

        this.activePopover = null;

        onWillStart(async () => {
            await this.loadAlarmStatus();

            this.intervalId = setInterval(() => {
                this.loadAlarmStatus();
            }, 15000);
        });

        onWillUnmount(() => {
            clearInterval(this.intervalId);

            if (this.activePopover) {
                this.activePopover();
            }
        });
    }

    async loadAlarmStatus(){
        try {
            const data = await this.orm.call("alarm.ukraine.locations", "get_alarm_status", [], {context: { silent: true } });

            const previousAlertStatus = this.state.alert;
            this.state.city = data.city;
            this.state.alert = data.alert;
            this.state.updated = this.formatDate(data.updated);

            if (!previousAlertStatus && this.state.alert) {
                this.triggerAutoPopover();
                this.playSirenSound(); // ЗВУКОВОЙ СИГНАЛ!
            }
        } catch (error) {
            console.error("Не вдалося отримати статус тривоги:", error);
        }
    }

    // Метод для воспроизведения звука
    playSirenSound() {
        try {
            // Формируем правильный путь к статическому аудио-файлу нашего модуля
            const soundUrl = "/alarm_ukraine/static/src/audio/siren.mp3";
            const audio = new Audio(soundUrl);

            // Настраиваем громкость от 0.0 до 1.0 (например, 0.7 - 70%)
            audio.volume = 0.7;

            // Запускаем воспроизведение
            audio.play();
        } catch (soundError) {
            console.warn("Браузер заблокировал автовоспроизведение звука до первого клика пользователя:", soundError);
        }
    }

    onIconClick(ev) {
        this.popover.add(ev.currentTarget, AlarmPopoverContent, {
            state: this.state,
        }, {
            closeOnClickOutside: true,
            position: "bottom",
        });
    }

     // Метод для автоматического открытия при тревоге
    triggerAutoPopover() {
        // Находим HTML-элемент нашего колокольчика в документе по ID, который мы добавим в XML
        const iconElement = document.getElementById("systray_alarm_icon");
        if (iconElement) {
            this.openPopover(iconElement);
        }
    }

    // Единый метод для открытия поповера
    openPopover(targetElement) {
        // Если поповер уже открыт на экране — ничего не делаем
        if (this.activePopover) {
            return;
        }

        // Сервис.add() возвращает функцию закрытия. Мы сохраняем её в this.activePopover
        this.activePopover = this.popover.add(targetElement, AlarmPopoverContent, {
            state: this.state,
        }, {
            closeOnClickOutside: true,
            position: "bottom",
            onClose: () => {
                // Когда пользователь закроет окно кликом мимо — очищаем ссылку
                this.activePopover = null;
            context: { silent: true }
            }
        });
    }

    formatDate(dateString) {
        if (!dateString) return "--:--";
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return "--:--";

        const pad = (number) => String(number).padStart(2, "0");

        return (
            `${pad(date.getDate())}.` +
            `${pad(date.getMonth() + 1)}.` +
            `${date.getFullYear()} ` +
            `${pad(date.getHours())}:` +
            `${pad(date.getMinutes())}`
        );
    }
}


SystrayAlarm.template = "alarm_ukraine.SystrayAlarm";

registry.category("systray").add("alarm_ukraine.systray_alarm", {
    Component: SystrayAlarm,
});
