## -*- coding: utf-8 -*-

#l_maszyn - liczba maszyn
#l_zestawow - liczba zestawow
#horyzont - horyzont analizy w dniach
#sr_t_awaria - sredni czas do awarii
#sr_t_naprawy - sredni czas naprawy
#uklad - "G" - gniazdowy, "L" - liniowy

import numpy as np
import time

def model(l_maszyn, l_zestawow, horyzont, sr_t_awaria, sr_t_naprawy, uklad):
    horyzont = horyzont * 24 *60
    #generowanie czasow pierwszych awarii
    #w numpy parametr skali podaje sie w formie 1/lambda - patrz
    #http://docs.scipy.org/doc/numpy-1.10.1/reference/generated/numpy.random.exponential.html
    #zdarzenia: awaria, otrzymanie narzedzia, naprawa
    zdarzenia = np.random.exponential(sr_t_awaria, l_maszyn)
    zdarzenia = list(map(int, zdarzenia))
    #wektor opisujacy status maszyn W - dziala, Q - czeka na zestaw i brak zestawu 
    #nr zestawu naprawczego ktory naprawia maszyne lub ktory zostal do niej zamowiony
    status_maszyn = []
    t_start = [] #poczatek bezczynnosci
    t_skum = [] #skumulowany czas bezczynnosci 
    for i in range(l_maszyn):
        status_maszyn.append("W")
        t_start.append(horyzont)
        t_skum.append(0)
    #lokalizacja zestawow, -1 - w warsztacie, nr maszyny
    lok_zestaw = []
    for i in range(l_zestawow):
        lok_zestaw.append(-1)
    #czas zwolnienia zestawu naprawczego, czas <= aktualny czas dla zestawu w warsztacie
    zwol_zestaw = []
    for i in range(l_zestawow):
        zwol_zestaw.append(0)
    t = min(zdarzenia) #zegar symulacji
    
    #symulacja od zdarzenia do zdarzenia
    while(t <= horyzont):
        #jezeli zestaw jest w warsztacie na moment t to ustaw lokalizacje na warsztat (-1)
        for i in range(l_zestawow):
            if zwol_zestaw[i] <= t:
                lok_zestaw[i] = -1
        #na ktorej maszynie wystapilo zdarzenie, maszyny numerowane od 0
        maszyna = zdarzenia.index(t)
        #jezeli status = W, to ustaw czas startu awarii w wektorze z awariami na maszynie
        #jezeli brak zestawu w warsztacie, to ustaw status Q, zaktualizuj wektor
        #z czasem zdarzen o najmniejszy czas zwolnienia zestawu
        #jezeli jest zestaw w warsztacie, to ustaw status = nr zestawu, zaktualizuj wektor 
        #z czasem zdarzen o czas dostawy + czas naprawy, lokalizacja zestawu = nr maszyny
        #czas zwolnienia zestawu = czas dostawy * 2 + czas naprawy
        if status_maszyn[maszyna] == "W":
            t_start[maszyna] = t
            dostepny_zestaw = -1
            for i in range(l_zestawow):
                if lok_zestaw[i] == -1:
                    dostepny_zestaw = i
                    break
            if dostepny_zestaw == -1:
                status_maszyn[maszyna] = "Q"
                zdarzenia[maszyna] = min(zwol_zestaw)
            else:
                status_maszyn[maszyna] = dostepny_zestaw
                if uklad == "G":
                    t_dostawy = 3
                else:
                    t_dostawy = 2 * (maszyna + 1)
                t_naprawy = int(np.random.gamma(3, sr_t_naprawy/3))
                #a += b <=> a = a + b
                zdarzenia[maszyna] += t_dostawy + t_naprawy
                lok_zestaw[dostepny_zestaw] = maszyna
                zwol_zestaw[dostepny_zestaw] = 2 * t_dostawy + t_naprawy + t        
        #jezeli status = Q, to teraz zamow narzedzia, czyli ustaw status = nr zestawu 
        #zaktualizuj wektor z czasem zdarzen o czas dostawy + czas naprawy, 
        #lokalizacja zestawu = nr maszyny, czas zwolnienia zestawu = 
        #czas dostawy * 2 + czas naprawy
        #tutaj zabezpieczamy sie na wypadek, gdyby nie bylo wolnego zestawu - najprawdopodobniej
        #mozna z tego zrezygnowac
        elif status_maszyn[maszyna] == "Q":
            dostepny_zestaw = -1
            for i in range(l_zestawow):
                if lok_zestaw[i] == -1:
                    dostepny_zestaw = i
                    break
            if dostepny_zestaw == -1:
                status_maszyn[maszyna] = "Q"
                zdarzenia[maszyna] = min(zwol_zestaw)
            else:
                status_maszyn[maszyna] = dostepny_zestaw
                if uklad == "G":
                    t_dostawy = 3
                else:
                    t_dostawy = 2 * (maszyna + 1)
            t_naprawy = int(np.random.gamma(3, sr_t_naprawy/3))
            zdarzenia[maszyna] += t_dostawy + t_naprawy
            lok_zestaw[dostepny_zestaw] = maszyna
            zwol_zestaw[dostepny_zestaw] = 2 * t_dostawy + t_naprawy + t
        #jezeli status rozny od Q lub W, to naprawiono, czyli ustaw status W, 
        #zaktualizuj wektor z czasem zdarzen o czas nastepnej awarii, policz czas skumulowany
        #bezczynnosci
        else:
            status_maszyn[maszyna] = "W"
            zdarzenia[maszyna] += np.random.exponential(sr_t_awaria)
            zdarzenia = list(map(int, zdarzenia))
            t_skum[maszyna] += t - t_start[maszyna]
            t_start[maszyna] = horyzont
            
        t = min(zdarzenia)
    #zwroc liste skumulowanych czasow bezczynnosci dla kazdej maszyny
        #print(status_maszyn,lok_zestaw,zwol_zestaw,t)
        #if zwol_zestaw[4]>0 and ty <5:
        #print(status_maszyn,lok_zestaw,zwol_zestaw,t)
            #ty += 1
    for i in range(l_maszyn):
        t_skum[maszyna] += horyzont - t_start[maszyna]
    return(t_skum)

def symulacja(l_symul, l_maszyn, l_zestawow, horyzont, sr_t_awaria, sr_t_naprawy, uklad):
    t_skum_symul = [] #lista list bedacych lacznym czasem bezczynnosci poszczegolnych 
                      #maszyn w symulacji   
    for i in range(l_symul):
        t_skum = model(l_maszyn, l_zestawow, horyzont, sr_t_awaria, sr_t_naprawy, uklad)
        t_skum_symul.append(t_skum)
    return(t_skum_symul)


l_symul = 100
l_maszyn = 6
l_zestawow = 4
horyzont = 30 #w dniach
sr_t_awaria = 75
sr_t_naprawy = 15

start_time = time.time()
t_skum_symul_L = symulacja(l_symul, l_maszyn, l_zestawow, horyzont, sr_t_awaria, 
                         sr_t_naprawy, "L")
t_skum_symul_G = symulacja(l_symul, l_maszyn, l_zestawow, horyzont, sr_t_awaria, 
                         sr_t_naprawy, "G")
end_time = time.time()
#print(t_skum_symul_L)
#print(t_skum_symul_G)

#skumulowany czas na wszystkich maszynach w symulacjach
t_skum_L = list(map(sum, t_skum_symul_L))
t_skum_G = list(map(sum, t_skum_symul_G))

print("Uklad liniowy")
print(t_skum_L)
print("Uklad gniazdowy")
print(t_skum_G)

time = end_time - start_time
print("Czas wykonywania: " + str(time) + " sekund, symulacji: " + str(l_symul) + 
        ", horyzont: " + str(horyzont))
