# program -> naredbe
# naredbe -> naredbe naredba | naredba
#
# naredba   -> pridruživanje
#            | print
#            | if
#
# pridruživanje -> IME# JEDNAKO izraz TOČKAZ
#
# print -> PRINT izraz TOČKAZ
#        | PRINT STRING# TOČKAZ
#        | PRINT NEWLINE TOČKAZ
#
# if    -> IF izraz THEN naredbe ENDIF
#        | IF izraz THEN naredbe ELSE naredbe ENDIF
#
# izraz -> OTV izraz ZATV
#        | izraz PLUS izraz
#        | izraz MINUS izraz
#        | izraz PUTA izraz
#        | izraz DIV izraz
#        | izraz MANJE izraz
#        | izraz VECE izraz
#        | izraz JMANJE izraz
#        | izraz JVECE izraz
#        | izraz JEDNAKO izraz
#        | izraz NEJEDNAKO izraz
#        | MINUS izraz
#        | BROJ#
#        | IME#
