# program -> naredbe
# naredbe -> naredbe naredba | naredba
# naredba   -> pridruživanje
#           | printanje
#           | if_naredba
# pridruživanje -> IME# JEDNAKO izraz TOČKAZ
# printanje -> PRINT izraz TOČKAZ
#            | PRINT STRING TOČKAZ
#            | PRINT NEWLINE TOČKAZ
# if_naredba    -> IF izraz THEN naredbe ENDIF
#               | IF izraz THEN naredbe ELSE naredbe ENDIF
# izraz -> OTV izraz ZATV
#       | izraz + izraz
#       | izraz - izraz
#       | izraz * izraz
#       | izraz / izraz
#       | izraz < izraz
#       | izraz > izraz
#       | izraz <= izraz
#       | izraz >= izraz
#       | izraz == izraz
#       | izraz != izraz
#       | - izraz
#       | BROJ
#       | IME
