```
start -> naredbe
naredbe -> naredbe naredba | naredba
naredba   -> pridruživanje
           | definiranje
           | definiranje_tipa
           | printanje
           | grananje
           | funkcija
           | vraćanje
           | match
           | INPUT IME#
           | IME# poziv
definiranje_tipa -> DATA VELIKOIME# MANJE parametri_tipa VECE AS konstruktori ENDDATA
                  | DATA VELIKOIME# AS konstruktori ENDDATA
parametri_tipa -> VARTIPA# | parametri_tipa ZAREZ VARTIPA#
konstruktori -> konstruktor | konstruktori ZAREZ konstruktor
konstruktor -> VELIKOIME# | OTV članovi_konstruktori ZATV
članovi_konstruktori -> tip | članovi_konstruktori ZAREZ tip
tip -> INT | BOOL | STRINGT | UNITT | VELIKOIME# | VARTIPA#
definiranje -> LET tipizirano JEDNAKO izraz TOČKAZ
tipizirano -> IME# OFTYPE tip
match -> MATCH izraz AS varijante ENDMATCH
varijante -> varijanta | varijante ZAREZ varijanta
varijanta -> VELIKOIME# poziv NAPRIJED naredba
poziv -> OTV ZATV | OTV argumenti ZATV
argumenti -> izraz | argumenti ZAREZ izraz
pridruživanje -> IME# JEDNAKO izraz TOČKAZ
printanje -> PRINT izraz TOČKAZ
           | PRINT STRING# TOČKAZ
           | PRINT NEWLINE TOČKAZ
grananje  -> IF izraz THEN naredbe ENDIF
           | IF izraz THEN naredbe ELSE naredbe ENDIF
vraćanje  -> VRATI TOČKAZ
           | VRATI izraz TOČKAZ
funkcija -> DEF ime OTV parametri ZATV FTYPE tip AS naredbe ENDDEF
parametri -> ime | parametri ZAREZ ime
izraz -> član
       | izraz PLUS član
       | izraz MINUS član
član -> faktor
      | član PUTA faktor
      | član DIV faktor
      | član MANJE faktor
      | član VECE faktor
      | član JMANJE faktor
      | član JVECE faktor
      | član JEDNAKO faktor
      | član NEJEDNAKO faktor
faktor    -> BROJ#
           | IME#
           | IME# poziv
           | OTV izraz ZATV
           | MINUS faktor
```