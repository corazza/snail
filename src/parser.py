## Beskontekstna gramatika
# start -> naredbe naredba
# naredbe -> '' | naredbe naredba
# naredba -> petlja | grananje | ispis TOČKAZ | BREAK TOČKAZ
# for -> FOR OOTV IME# JEDNAKO BROJ TOČKAZ IME# MANJE BROJ TOČKAZ
# 	     IME# inkrement OZATV
# petlja -> for naredba | for VOTV naredbe VZATV
# inkrement -> PLUSP | PLUSJ BROJ
# ispis -> COUT varijable | COUT varijable MMANJE ENDL
# varijable -> '' | varijable MMANJE IME
# grananje -> IF OOTV IME JJEDNAKO BROJ OZATV naredba


# program -> naredbe
# naredbe -> naredbe naredba | naredba
# stmt -> assign_stmt
#       | print_stmt
#       | if_stmt
#       | while_stmt
# assign_stmt -> ID = expr ;
# print_stmt -> PRINT expr ;
#            | PRINT string ;
#            | PRINT NEWLINE ;
# if_stmt -> IF expr THEN stmt_list ENDIF
#           | IF expr THEN stmt_list ELSE stmt_list ENDIF
# while_stmt -> WHILE expr DO stmt_list ENDWHILE
# expr -> ( expr )
#       | expr + expr
#       | expr - expr
#       | expr * expr
#       | expr / expr
#       | expr < expr
#       | expr > expr
#       | expr <= expr
#       | expr >= expr
#       | expr == expr
#       | expr != expr
#       | - expr
#       | INT
#       | ID