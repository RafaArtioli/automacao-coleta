from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
import pandas as pd
import time


class Fedex:

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("start-maximized")
        
        self._driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        self._action = ActionChains(self._driver)
        self._wait = WebDriverWait(self._driver, 50)
        self._wait_quickly = WebDriverWait(self._driver,10)

    def get_url(self, url):
        self._driver.get(url)

    def tipo_cliente(self):
        #Destinatário
        try:
            tipo = self._wait_quickly.until(EC.presence_of_element_located((By.ID, 'remDest')))
            tipo.click()
            time.sleep(1)
            selecionar = self._wait_quickly.until(EC.presence_of_element_located((By.XPATH, '//*[@id="remDest"]/div/div[3]/div/ul/p-dropdownitem[2]/li')))
            selecionar.click()
        except Exception as e:
            print(e)

    def pesquisar_cnpj(self,cnpj):
        try:
            cnpj_doc = self._wait_quickly.until(EC.presence_of_element_located((By.ID,'nrIdentificacao')))
            cnpj_doc.click()
            cnpj_doc.send_keys(cnpj)
        except Exception as e:
            print(e)
    
    def tipo_documento(self):
        #Nota fiscal
        try:
            tipo = self._wait_quickly.until(EC.presence_of_element_located((By.ID, 'tpDocumento')))
            tipo.click()
            time.sleep(1)
            nf = self._wait_quickly.until(EC.presence_of_element_located((By.XPATH, '//*[@id="tpDocumento"]/div/div[3]/div/ul/p-dropdownitem[2]')))
            nf.click()
        except Exception as e:
            print(e)

    def num_documento(self, notafiscal):
        try:
            num = self._wait_quickly.until(EC.presence_of_element_located((By.ID, 'nrDocumento')))
            num.click()
            num.send_keys(notafiscal)
        except Exception as e:
            print(e)
    
    def buscar_botao(self):
        try:
            buscar = self._wait_quickly.until(EC.presence_of_element_located((By.XPATH, '/html/body/app-root/app-menu/div[2]/app-tracking/div[1]/div[2]/button[1]')))
            buscar.click()
        except Exception as e:
            print(e)
        
    def clicar_nf(self):
        try:
            nf = self._wait_quickly.until(EC.presence_of_element_located((By.XPATH,'/html/body/app-root/app-menu/div[2]/app-tracking/div[2]/p-table/div/div[1]/table/tbody/tr/td[1]/a')))
            nf.click()
        except Exception as e:
            print(e)
    
    def texto_nf(self):
        try:
            texto = self._wait_quickly.until(EC.presence_of_element_located((By.XPATH, '/html/body/app-root/app-menu/div[2]/app-localizacao-simplicada-detail/div/div[2]/div[2]/div[1]/p-table/div/div[2]/table/tbody/tr[1]')))
            print(texto.text)
            time.sleep(0.5)
            texto2 = self._wait_quickly.until(EC.presence_of_element_located((By.XPATH,'/html/body/app-root/app-menu/div[2]/app-localizacao-simplicada-detail/div/div[2]/div[2]/div[1]/p-table/div/div[2]/table/tbody/tr[2]')))
            print(texto2.text)

            primeiro = texto.text.split(' ')
            segundo = texto2.text.split(' ')

            return primeiro[0], primeiro[3], segundo[0], segundo[2], segundo[5]

        except Exception as e:
            print(e)
            return None

    def voltar_botao(self):
        try:
            voltar = self._wait_quickly.until(EC.presence_of_element_located((By.XPATH, '/html/body/app-root/app-menu/div[2]/app-localizacao-simplicada-detail/div/div[3]/button/span')))
            voltar.click()
        except Exception as e:
            print(e)

    def teste_registro(self):
        try:
            error = self._wait_quickly.until(EC.presence_of_element_located((By.XPATH, '/html/body/app-root/app-menu/div[2]/app-tracking/div[2]/p-table/div/div[2]')))
            print(error.text)
            if error.text == "Nenhum registro encontrado.":
                nova_consulta = self._wait_quickly.until(EC.presence_of_element_located((By.XPATH, '/html/body/app-root/app-menu/div[2]/app-tracking/div[1]/div[2]/button[2]')))
                nova_consulta.click()
                return True
            else:
                self.clicar_nf()
                return False
        except Exception as e:
            print(e)

def main():
    fedex = Fedex()
    fedex.get_url(URL_FEDEX)
    time.sleep(1)

    df = pd.read_csv('base.csv', sep=";", on_bad_lines='skip')
    notafiscal = df["NOTAFISCAL"]
    cnpj = df["CNPJ"]

    result_df = pd.DataFrame(columns=['Nota Fiscal', 'CNPJ','Data prevista', 'Status entrega', 'Data entrega'])

    for notaf, cnpjj in zip(notafiscal, cnpj):
        fedex.tipo_cliente()
        fedex.pesquisar_cnpj(cnpjj)
        fedex.tipo_documento()
        fedex.num_documento(notaf)
        fedex.buscar_botao()
        time.sleep(1)

        erro = fedex.teste_registro()
        dados = {'Nota Fiscal': notaf, 'CNPJ': cnpjj}
        if erro:
            result_df = result_df._append({**dados, 'Data prevista': 'Nenhum registro encontrado.', 'Status entrega': '', 'Data entrega': ''},
                                         ignore_index=True)
            continue
        else:
            time.sleep(1)
            texto_nf_result = fedex.texto_nf()

            if texto_nf_result is None:
                print(f"Erro ao obter informações para CNPJ {cnpjj}")
                continue

            time.sleep(1)
            data, _, status_ent, _, data_ent = fedex.texto_nf()
            time.sleep(0.5)
            fedex.voltar_botao()
            time.sleep(1.5)

            result_df = result_df._append({**dados, 'Data prevista': data, 'Status entrega': data_ent, 'Data entrega': status_ent},
                                         ignore_index=True)
        

    result_df.to_csv('resultado.csv', sep=';', encoding='utf-8-sig', index=False)
    fedex._driver.quit()

main()
