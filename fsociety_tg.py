import random
import time
import re
import smtplib
import socks
import socket
import json
import sys
import os
from colorama import init, Fore, Style
import datetime
import warnings

# Ребят мой первый серьёзный проект поэтому если что сорян
init(autoreset=True)
warnings.filterwarnings("ignore", category=UserWarning, module="socks")
socket.setdefaulttimeout(10)

class FsocietySnatcher:
    def __init__(self):
        self.initialize_required_files()  
        self.reasons = {
            1: "осквернение религий",
            2: "продажа наркотиков",
            3: "оскорбления",
            4: "пробив личной информации",
            5: "распространение порно",
            6: "угрозы смерти",
            7: "другое"
        }
        self.complaint_templates = {
            1: "Пользователь Telegram @{username} публикует богохульный контент: {message_link}",
            2: "Обнаружена продажа запрещенных веществ через аккаунт @{username}: {message_link}",
            3: "Аккаунт @{username} систематически оскорбляет пользователей: {message_link}",
            4: "Пользователь @{username} занимается сливом персональных данных: {message_link}",
            5: "Распространение порнографии через аккаунт @{username}: {message_link}",
            6: "@{username} открыто угрожает физической расправой: {message_link}",
            7: "Аккаунт @{username} нарушает правила платформы: {message_link}"
        }
        
        
        self.blue_to_pink = [Fore.BLUE, Fore.LIGHTBLUE_EX, Fore.CYAN, 
                           Fore.LIGHTCYAN_EX, Fore.MAGENTA, Fore.LIGHTMAGENTA_EX]
        
        
        self.smtp_accounts = self.load_smtp_accounts()
        self.user_agents = self.load_user_agents()
        self.proxies = self.load_and_test_proxies()
        
        # Статистика
        self.success_count = 0
        self.total_count = 0

    def initialize_required_files(self):
        """Создает необходимые файлы при первом запуске"""
        if not os.path.exists("user_agents.txt"):
            with open("user_agents.txt", "w") as f:
                f.write("\n".join([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
                ]))
        
        if not os.path.exists("socks5_proxies.txt"):
            with open("socks5_proxies.txt", "w") as f:
                f.write("# Пример файла SOCKS5 прокси (формат: host:port)\n")
                f.write("proxy1.example.com:1080\n")
                f.write("proxy2.example.com:1080\n")
                f.write("# Добавьте свои рабочие прокси вместо этих примеров\n")

    def load_smtp_accounts(self):
        """Загрузка SMTP аккаунтов"""
        try:
            with open("smtp_accounts.json", "r") as f:
                return json.load(f)
        except Exception as e:
            self.print_error(f"Ошибка загрузки SMTP: {str(e)}")
            return []

    def load_user_agents(self):
        """Загрузка User-Agents"""
        try:
            with open("user_agents.txt", "r") as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.print_error(f"Ошибка загрузки User-Agents: {str(e)}")
            return []

    def load_and_test_proxies(self):
        """Загрузка и проверка прокси"""
        try:
            if not os.path.exists("socks5_proxies.txt"):
                return []
                
            with open("socks5_proxies.txt", "r") as f:
                proxies = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split(':')
                        if len(parts) == 2:
                            proxies.append({
                                'host': parts[0].strip(),
                                'port': int(parts[1].strip()),
                                'username': None,
                                'password': None
                            })
                
                # Тут прога проверяет рандом прокси чтобы удостовериться в надёжности прокси
                test_proxies = random.sample(proxies, min(10, len(proxies)))
                working_proxies = []
                
                self.print_gradient("\n[+] Проверка прокси...", start_blue=True)
                for proxy in test_proxies:
                    if self.test_proxy(proxy):
                        working_proxies.append(proxy)
                        print(f"{proxy['host']}:{proxy['port']} {Fore.GREEN}✓{Style.RESET_ALL}")
                    else:
                        print(f"{proxy['host']}:{proxy['port']} {Fore.RED}✗{Style.RESET_ALL}")
                    time.sleep(0.5)
                
                self.print_gradient(f"[+] Рабочих прокси: {len(working_proxies)}/{len(test_proxies)}", start_blue=True)
                return working_proxies if working_proxies else proxies[:10]  # Возвращаем все, если не удалось проверить
                
        except Exception as e:
            self.print_error(f"Ошибка загрузки прокси: {str(e)}")
            return []

    def test_proxy(self, proxy):
        """Проверка работоспособности прокси"""
        try:
            socks.set_default_proxy(socks.SOCKS5, proxy['host'], proxy['port'])
            socket.socket = socks.socksocket
            test_socket = socket.create_connection(("www.google.com", 80), timeout=10)
            test_socket.close()
            return True
        except:
            return False

    def print_gradient(self, text, start_blue=False):
        """Вывод градиентного текста"""
        colors = self.blue_to_pink if start_blue else list(reversed(self.blue_to_pink))
        colored_text = ""
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            colored_text += color + char
        print(colored_text + Style.RESET_ALL)

    def print_error(self, message):
        """Вывод сообщения об ошибке"""
        print(Fore.RED + f"[!] {message}" + Style.RESET_ALL)

    def print_fsociety_banner(self):
        """Вывод баннера программы"""
        banner = r"""
  ######   #####    #####     ####    ####    #######  ######   ##  ##
  ##   #  ##   ##  ##   ##   ##  ##    ##      ##   #  # ## #   ##  ##
  ## #    #        ##   ##  ##         ##      ## #      ##     ##  ##
  ####     #####   ##   ##  ##         ##      ####      ##      ####
  ## #         ##  ##   ##  ##         ##      ## #      ##       ##
  ##      ##   ##  ##   ##   ##  ##    ##      ##   #    ##       ##
 ####      #####    #####     ####    ####    #######   ####     ####  
        """
        
        print("\n" + "=" * 60)
        self.print_gradient(" TELEGRAM ACCOUNT SNATCHER PRO ".center(60, '~'), start_blue=True)
        print("=" * 60)
        print(banner)
        print("=" * 60)
        self.print_gradient(f" SMTP: {len(self.smtp_accounts)} | SOCKS5: {len(self.proxies)} ".center(60), start_blue=True)
        print("=" * 60 + "\n")

    def get_complaint_details(self):
        """Интерактивный ввод данных"""
        while True:
            try:
                print("\nВыберите причину нарушения:")
                for num, reason in self.reasons.items():
                    print(f"{num}. {reason}")
                
                choice = int(input("> "))
                if 1 <= choice <= 7:
                    break
                self.print_error("Введите число от 1 до 7")
            except ValueError:
                self.print_error("Некорректный ввод")
        
        while True:
            username = input("Введите юзернейм нарушителя (@username): ")
            if re.match(r"^@[a-zA-Z0-9_]{5,32}$", username):
                break
            self.print_error("Формат: @username (5-32 символов)")
        
        while True:
            message_link = input("Ссылка на сообщение с нарушением: ")
            if re.match(r"^https?://t\.me/[a-zA-Z0-9_\-/]+/\d+$", message_link):
                break
            self.print_error("Формат: https://t.me/chatname/123")
        
        return choice, username, message_link

    def send_complaint(self, smtp_acc, proxy, user_agent, username, message_link, reason_id):
        """Отправка жалобы"""
        try:
            socks.set_default_proxy(socks.SOCKS5, proxy['host'], proxy['port'])
            socket.socket = socks.socksocket
            
            subject = f"Жалоба на пользователя {username}"
            body = self.complaint_templates[reason_id].format(
                username=username,
                message_link=message_link
            )
            
            with smtplib.SMTP(smtp_acc['server'], smtp_acc['port'], timeout=15) as server:
                server.starttls()
                server.login(smtp_acc['login'], smtp_acc['password'])
                server.sendmail(
                    smtp_acc['login'], 
                    'abuse@telegram.org', 
                    f"Subject: {subject}\n\n{body}"
                )
            return True
        except Exception as e:
            self.print_error(f"Ошибка отправки: {str(e)}")
            return False

    def run_campaign(self, username, message_link, reason_id):
        """Запуск кампании"""
        if not self.smtp_accounts:
            self.print_error("Не найдено SMTP аккаунтов (создайте smtp_accounts.json)")
            return
        if not self.proxies:
            self.print_error("Не найдено рабочих прокси (проверьте socks5_proxies.txt)")
            return
        
        self.print_gradient("\n[+] Начинаем операцию...", start_blue=True)
        print(f"Цель: {username}")
        print(f"Нарушение: {self.reasons[reason_id]}")
        
        self.success_count = 0
        self.total_count = min(50, len(self.smtp_accounts))
        start_time = datetime.datetime.now()
        
        for i in range(self.total_count):
            smtp_acc = random.choice(self.smtp_accounts)
            proxy = random.choice(self.proxies)
            user_agent = random.choice(self.user_agents)
            
            print(f"\nЖалоба #{i+1}/{self.total_count}:")
            print(f"SMTP: {smtp_acc['server']}")
            print(f"Прокси: {proxy['host']}:{proxy['port']}")
            
            if self.send_complaint(smtp_acc, proxy, user_agent, username, message_link, reason_id):
                self.success_count += 1
                print(Fore.GREEN + "[✓] Успешно отправлено")
            else:
                print(Fore.RED + "[!] Ошибка отправки")
            
            time.sleep(1)
        
        elapsed = datetime.datetime.now() - start_time
        print("\n" + "=" * 60)
        self.print_gradient(" РЕЗУЛЬТАТЫ ".center(60, '~'), start_blue=True)
        print(f"Успешных жалоб: {self.success_count}/{self.total_count}")
        print(f"Затраченное время: {str(elapsed).split('.')[0]}")
        print("=" * 60)

    def run(self):
        """Главная функция"""
        try:
            self.print_fsociety_banner()
            reason_id, username, message_link = self.get_complaint_details()
            self.run_campaign(username, message_link, reason_id)
        except KeyboardInterrupt:
            self.print_error("\nОперация прервана пользователем")
        except Exception as e:
            self.print_error(f"\nКритическая ошибка: {str(e)}")
        finally:
            print("\n" + "=" * 60)
            print(" Программа завершена ".center(60, '~'))
            print("=" * 60)

if __name__ == "__main__":
    try:
        snatcher = FsocietySnatcher()
        snatcher.run()
    except ImportError as e:
        print(Fore.RED + f"[!] Ошибка: {str(e)}")
        print(Fore.YELLOW + "Установите зависимости командой:")
        print(Fore.CYAN + "pip install PySocks colorama" + Style.RESET_ALL)
        sys.exit(1)