# Importa as bibliotecas necessárias do Selenium para automação de navegador
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Gerenciador automático do ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager

# Biblioteca para pausas e controle de tempo
import time

# pyautogui para janelas de confirmação e entrada de dados
import pyautogui as pa

# Pergunta ao usuário se deseja configurar ou desconfigurar o roteador
config = pa.confirm('Deseja Configurar ou Desconfigurar?', 'config', ['Configurar', 'Desconfigurar'])

# Coleta as informações de configuração ou define valores padrão se for para desconfigurar
if config == 'Configurar':
    nome = pa.prompt('Qual o nome(ssid) do roteador?', 'SSID')
    senha = pa.prompt('Qual a senha do roteador?', 'Senha')
    n_conexoes = int(pa.prompt('Qual o numero de conexoes?', 'conexoes'))
    dhcp_confirm = pa.confirm(text='Deseja mudar o DHCP?', title='dhcp', buttons=['Sim', 'Não'])
else:
    nome = '#WIFI.LEGAL'      # SSID padrão
    senha = '123Legal'        # Senha padrão
    n_conexoes = 10           # Número padrão de conexões
    dhcp_confirm = 'Não'      # Não alterar DHCP

# Configura o navegador Chrome com WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Define um tempo de espera explícito
wait = WebDriverWait(driver, 10)

# Acessa a página do roteador
driver.get('http://192.168.1.1')

# Pequena pausa para garantir carregamento
time.sleep(0.5)

# Aguarda o campo de usuário aparecer e preenche com 'admin'
wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys('admin')

# Preenche a senha e faz login
driver.find_element(By.ID, 'password').send_keys('@40legal')
driver.find_element(By.ID, 'login').click()

# Espera a tela de carregamento desaparecer
wait.until(EC.invisibility_of_element((By.CLASS_NAME, 'xtiper_bg_white')))

# Clica no link para Modo Avançado via JavaScript (para garantir clique)
element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Modo Avançado')))
driver.execute_script("arguments[0].click();", element)

# Tenta clicar na configuração de Wi-Fi, com fallback se estiver em outro menu
try:
    wait.until(EC.element_to_be_clickable((By.ID, 'Wifi_Configuration'))).click()
except:
    wait.until(EC.element_to_be_clickable((By.ID, 'Configuration'))).click()
    wait.until(EC.element_to_be_clickable((By.ID, 'Wifi_Configuration'))).click()

# Troca para o iframe que contém o formulário de configuração
wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iframe_wrap")))

# Aguarda o campo SSID carregar
wait.until(EC.presence_of_element_located((By.ID, 'wifi2GSSID')))

# Pausa para garantir carregamento do conteúdo
time.sleep(2)

# Altera o SSID (nome da rede Wi-Fi)
ssid = driver.find_element(By.ID, 'wifi2GSSID')
ssid.click()
ssid.send_keys(Keys.CONTROL + 'a')  # Seleciona tudo
ssid.send_keys(nome)                # Digita o novo nome

# Altera a senha da rede Wi-Fi
wait.until(EC.presence_of_element_located((By.ID, 'wifi2GPassword')))
password = driver.find_element(By.ID, 'wifi2GPassword')
password.send_keys(Keys.CONTROL + 'a')
password.send_keys(senha)

# Atualiza o número máximo de conexões simultâneas via script JS
driver.execute_script(f"""
    if (typeof writeMaxClientRangeElement === 'function') {{
        let slider = document.getElementById('range');
        slider.value = {n_conexoes};
        slider.dispatchEvent(new Event('input'));
        slider.dispatchEvent(new Event('change'));
        document.getElementById('wifi2GMaxClientNum').innerText = {n_conexoes};
    }}
""")

# Espera antes de aplicar
time.sleep(1)

# Aplica as configurações de Wi-Fi
driver.find_element(By.ID, 'Wifi2GApply').click()

# Sai do iframe para acessar o botão de confirmação
driver.switch_to.default_content()

# Clica no botão "OK" após aplicar as configurações
wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='OK']"))).click()

# Se o usuário escolheu alterar o DHCP:
if dhcp_confirm == 'Sim':
    time.sleep(1.5)
    
    # Garante que está fora do iframe
    driver.switch_to.default_content()
    
    # Acessa o menu de configuração de LAN
    driver.find_element(By.ID, 'Lan_Configuration').click()

    # Troca para o iframe da LAN
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iframe_wrap")))

    # Espera o campo de IP final carregar
    wait.until(EC.presence_of_element_located((By.ID, 'LANEndIP')))

    # Altera o DHCP para terminar no IP baseado no número de conexões
    dhcp = driver.find_element(By.ID, 'LANEndIP')
    dhcp.send_keys(Keys.CONTROL + 'a')
    dhcp.send_keys(f'192.168.1.{101+n_conexoes}')
    
    # Aplica as mudanças
    driver.find_element(By.ID, 'apply').click()

# Mostra mensagem de sucesso
pa.alert('SUCESSO')