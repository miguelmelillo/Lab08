from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        lista_prezzi_media = []
        for d in self._distributori:
            d.get_prezzi()
            prezzi = 0
            num_prezzi = 0
            for p in d.lista_prezzi: # lista con oggetti di tipo prezzo, con attr tipo datetime.date
                if p.data.month == mese:
                    num_prezzi += 1
                    prezzi += p.prezzo_litro
            media = (prezzi / num_prezzi)
            lista_prezzi_media.append((d.nome, media))
        return lista_prezzi_media


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__sequenza_ottima, self.__costo_ottimo = self.__ricorsione([], 1, None, 0, prezzi_settimana)
        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if giorno > 7:
            return sequenza_parziale, costo_corrente
        distributore_prezzo = [] # dove voglio salvare liste [distributore, prezzo_aggiornato] e poi ordinarle in base ai prezzi
        for d in prezzi_settimana: # prezzi_settimana è un dict di liste
            if d == ultimo_distributore or ultimo_distributore is None: # se il distributore è il primo del mese oppure lo stesso del giorno precedente
                distributore_prezzo.append([d, float(prezzi_settimana[d][giorno-1])*100])
            else:
                distributore_prezzo.append([d, float(prezzi_settimana[d][giorno-1])*100 + 5]) # +5 perché c'è il cambio del distributore
        distributore_prezzo = sorted(distributore_prezzo, key=lambda x: x[1], reverse=False) # ordino la lista di liste, poi utilizzo solo la prima delle liste ([0])
        sequenza_parziale.append(distributore_prezzo[0][0])
        ultimo_distributore = distributore_prezzo[0][0]
        costo_corrente += distributore_prezzo[0][1]
        giorno += 1
        sequenza_parziale, costo_corrente = self.__ricorsione(sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana)
        return sequenza_parziale, costo_corrente

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        dict_prezzi_settimana = {}
        for d in self._distributori:
            d.get_prezzi()
            if d.id not in dict_prezzi_settimana:
                dict_prezzi_settimana[d.id] = [p.prezzo_litro for p in d.lista_prezzi if p.data.month == mese and p.data.day in range(1,8)]
        return dict_prezzi_settimana



