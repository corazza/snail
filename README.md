# Snaskell

Naša implementacija [Snaila](https://www.cs.rpi.edu/courses/fall01/modcomp/project2.pdf) koju zovemo Snaskell je inspirirana Haskellom i proširuje Snail dodavanjem sljedećih mogućnosti.

1. Korisnički tipovi podataka i type checking
2. Polimorfizam (templates/generics)
3. Jednostavni pattern matching
4. Definiranje funkcija (može rekurzivnih) i opcionalna memoizacija

Kako je navedeno u zadatku, konstrukti za petlje (while, for) su izbačeni.

Primjer (`python snail.py ../primjeri/liste.snail` u `src/`):

```
=== typechecking ===
print:  (A) -> unit
println:  (A) -> unit
input:  () -> string
to_int:  (string) -> int
None:  Option<_>
Some:  (A) -> Option<A>
Nil:  List<_>
Concat:  (A, List<A>) -> List<A>
head:  (List<A>) -> Option<A>
unesi_element:  (int, List<A>) -> List<A>
unesi_n_elemenata_rek:  (List<A>, int) -> List<A>
unesi_n_elemenata:  (int) -> List<int>
n:  int
lista:  List<int>

=== pokretanje ===
Unesite broj elemenata: 3
Unesite element 3: 754
Unesite element 2: 34
Unesite element 1: 6
Unesena lista:
Concat(6, Concat(34, Concat(754, Nil)))
Prvi element: 6
```

Naravno mogućnosti Snaskella su ograničene u usporedbi s pravim sustavima:

1. (Skoro) sve oznake tipova se moraju eksplicitno pisati, dok se u Hindley–Milner sistemu (kojeg Haskell proširuje) ne mora nijedna.
2. Varijable tipova, koje ostvaruju polimorfizam, ne mogu se restringirati (type klase u Haskellu dodaju tu mogućnost).
3. Kod pattern matchinga, obrasci ne mogu biti proizovoljne vrijednosti (dobrog tipa), već samo konstruktori koji eksplicitno navode slobodne varijable.

U direktorijima `std/` i `primjeri/` se mogu vidjeti demonstracije navedenih mogućnosti, koje ćemo sada detaljnije objasniti.

## Korisnički tipovi

Korisnički tipovi se definiraju koristeći `data ... as ... enddata` sintaksu,
što ćemo pokazati kroz primjer tipa `Option`.
Između `as` i `enddata` nalazi se popis konstruktora za tip.
Konstruktor sadrži popis 0 ili više tipova, koji čine polja konstruktora.

```
data Option<A> as   // Option je ime tipa, A je varijabla tipa (npr. A == int)
    None,           // konstruktor bez argumenata
    Some(A)         // konstruktor s jednim argumentom tipa A
enddata
```

`Option<A>` se može shvatiti kao spremnik koji može ili biti prazan (`None`)
ili sadržavati točno jednu vrijednost tipa `A` (`Some`).
`Option<A>` može poslužiti za predstavljanje rezultata operacija koje ne moraju uspjeti.

Tijelo definicije `Option` sadrži dva konstruktora, `None` i `Some`.
Konstruktor `None` se može shvatiti kao vrijednost tipa `Option<A>` za bilo koji `A` (tj. `None : Option<_>`),
a `Some` se može shvatiti kao funkcija koja prima `A` i vraća `Option<A>`.

`A` je varijabla tipa i odnosi se na neki konkretni tip, poput `int` ili `string`.
Na primjer, vrijednost `Some(1)` je tipa `Option<int>`.

Moguće je definirati rekurzivne strukture podataka:

```
data List<A> as
    Nil,
    Concat(A, List<A>)
enddata
```

`Nil` predstavlja bazni slučaj (praznu listu),
a `Concat(A, List<A>)` predstavlja nepraznu listu dobivenu dodavanjem vrijednosti tipa `A` na početak liste tipa `List<A>`.

Kroz dodatni primjer korisničkog tipa `Pair` (iz datoteke `std/parovi.snail`) ističemo da se u definicijama može pojavljivati više parametara tipa:

```
data Pair<C, D> as
    Pa(C, D)
enddata
```

Ovaj tip ima samo jedan konstruktor koji se zove `Pa`
(trebao bi se zvati `Pair` ali ne može radi tehničke limitacije koja nije bila prioritetna).
`Pa` prima dva izraza te ih stavlja u "produkt",
tako da ta složena vrijednosti i prvog i drugog izraza.
Ti izrazi mogu ali ne moraju biti različitih tipova.

## Pattern matching

Korisnički tipovi podataka u Snaskellu imaju oblik "sume produkta" tipova,
u smislu da su konstruktori članovi sume, a polja konstruktora faktori produkta.
U ovom kontekstu, suma se može shvatiti kao *ili* (`List<A>` je ili `Nil` ili `Concat`),
a produkt se može shvatiti kao *i* (`Concat(A, List<A>)` sadrži i `A` i `List<A>`).
Takva algebarska interpretacija tipova umjesto klasične `case` sintakse iz C-ovskih jezika omogućava ekspresivniju konstrukciju pattern matchinga,
koja pomaže u kontroli toka,
pristupanju poljima, i pokrivanju relevantnih slučajeva na vizualno intuitivan način.

To ćemo demonstrirati na primjeru funkcije `head(xs: List<A>) -> Option<A>` koja vraća prvi element liste (ako postoji):

```
def head(xs: List<A>) -> Option<A> as
    match xs as
        Concat(x, tail) => return Some(x),
        Nil => return None
    endmatch
enddef
```

Ulazna lista `xs` može biti ili prazna (bazni `Nil` slučaj) ili konkatenacija nekog `A` s listom `A`-ova.
Match naredba prima neku složenu vrijednost (tj. instancu tipa koji ima konstruktore, u ovom slučaju `xs`).
Tijelo match naredbe sadrži nizove oblika *pattern => naredba*.
Pattern mora biti jedan od konstruktora tipa kojeg ima složena vrijednost `match` naredbe,
preciznije pattern je "oblik" konstruktora koji umjesto argumenata koje treba izvrijedniti uvodi nove varijable.
U gornjem primjeru pattern `Concat(x, tail)` uvodi varijable `x` i `tail`.
Kažemo da se vrijednost dana matchu (`xs`) poklapa s nekim patternom ako je sastavljana od istog konstruktora na koji se odnosi pattern.
Npr. ako je dani `xs == Concat(1, Nil)`, on se poklapa s patternom `Concat(x, tail)` i ne s `Nil`.
Ako se dana vrijednost poklapa s patternom
izvršit će se uz taj pattern vezana naredba tako da se  varijable iz patterna uvedu u scope i vežu za dijelove dane vrijednosti
(`x` će u naredbi imati vrijednost `1`, a `tail` vrijednost `Nil`).

Type checking će se pobrinuti da su pokriveni svi slučajevi (konstruktori)
i da su to samo oni koji odgovaraju tipu dane vrijednosti.
Korist takve restrikcije je najbolje vidljiva na sljedećem primjeru koji analizira povratnu vrijednost `head` funkcije (`primjeri/liste.snail`):

```
print("Prvi element: ");

match head(lista) as
    None => print("nema ga"),
    Some(x) => print(x)
endmatch
```

Kad bi funkcionalnost `head`a implementirali u klasičnim programskim jezicima poput C-a ili Pythona
(najčešće) ne bi mogli biti sigurni da pozivatelji provjeravaju slučaj u kojemu `head` vrati null pointer ili `None`,
ali Snaskell program u kojemu se to ne provjerava neće proći type checking.

Nažalost ovo je daleko od pune moći koju se inače očekuje od pattern matchinga,
a to je da se umjesto ovako usko definiranih patterna mogu koristiti proizvoljni izrazi,
tj. da se dopusti da istovremeno postoje patterni
`Concat(x, tail)`, `Concat(f(a), Nil)`, `Concat(x, Concat(y, Nil))` i slično.

Slično funkciji `head`, za pristup elementima para koriste se funkcije `first` i `second`:

```
def first(p: Pair<A, B>) -> A as
    match p as
        Pa(a, b) => return a
    endmatch
enddef

def second(p: Pair<A, B>) -> B as
    match p as
        Pa(a, b) => return b
    endmatch
enddef
```

Kao uvod u sljedeću sekciju o type checkingu,
napominjemo da kad bi se u definiciji `first` linija `Pa(a, b) => return a` izmijenila u
`Pa(a, b) => return b`, Snaskell bi javio grešku **prije** izvođenja:

```
vepar.SemantičkaGreška: funkcija first treba vratiti A (dano: B)
```

## Type checking

Type checking se odvija prije izvršavanja programa i osigurava sljedeće.

1. Dani argumenti se u tipu poklapaju s parametrima funkcija i konstruktora.
2. Funkcije vraćaju vrijednost dobrog tipa (kakav je definiran).
3. Obrasci u match izrazima pokrivaju sve konstruktore, i samo konstruktore tog tipa.
4. Lijeva i desna strana pridruživanja se poklapaju u tipu.
5. Etc. (`if` testira izraz koji je tipa `bool`, ...)

Na primjeru:

```
println(Concat(1, Concat(2, Nil))); // OK
// println(Concat(1, Concat("asdf", Nil))); // type error!
```

Ovaj kod ispisuje `Concat(1, Concat(2, Nil))`.
No kada bi dekomentirali drugu liniju ne bi prošao type checking:

```
vepar.SemantičkaGreška: STRINGT'string' nije INT'int'
```

Poruka nije najjasnija ali odnosi se na napoklapanje u parametrima konstruktora `Concat`:
pokušavamo `1` (`int`) staviti na početak liste `Concat("asdf", Nil)` koja je tipa `List<string>`.

Type checking u Snaskellu je znatno olakšan činjenicom da svaka
funkcija i konstruktor u definiciji moraju navesti tipove svih parametara (ili navesti varijablu tipa).
Isto vrijedi i za definiranje varijabli (`let` naredba), gdje se mora navesti tip varijable.
Zato ne trebamo koristiti složenije metode određivanja tipova (type inference) nego uglavnom možemo konzultirati definicije i provjeriti poklapanje.

Jedina kompliciranija stvar u implementaciji type checkinga bile je provjeravanje da se
parametri tipa (`A`, `B`, etc.) konzistentno koriste.
Naime, definicija liste nigdje ne navodi što je tipa elemenata konkretno,
no type checking i dalje mora moći detektirati da on nije konzistentno korišten u izrazima
poput `Concat(1, Concat("asdf", Nil))`.
To je ostvarno tako da se na mjestima poziva (kako funkcija tako i konstruktora),
parametri tipa zamijene s korištenim tipovima (ili pak drugim parametrima tipa!)
te da se te zamjene pamte u mapiranju (iz varijabli tipa u uniju varijabli tipa i konkretnih tipova).
To mapiranje pazi na konzistentnost i javlja type error kad je prekršena.
Dio ove funkcionalnosti implementiran je u datoteci `src/tipovi.py`,
a dio u samim AST-ovima u `typecheck()` metodama.
`tipovi.py` sadrži općenite operacije poput instanciranja konkretnih tipova iz poziva,
izgradnje spomenute mape, rekurzivne provjere ekvivalentnosti složenih tipova, itd.,
dok AST-ovi sadrže dio logike koji je vezan uz njihovo značenje:
npr. to da deklarirani povratni tip funkcije mora biti isti kao tip izraza u return naredbi
je dio typecheck metode AST-a `Funkcija`.

Na kraju napominjemo da po primjeru Haskella i Rusta,
svaka funkcija u Snaskellu mora vratiti _nešto_,
tj. mora vratiti vrijednost dobrog tipa i nema opciju vraćanja ničega
(poput C-ovskih void funkcija).
U tu svrhu postoji tip `unit` koji ima samo jednu vrijednost `UNIT` i ne prenosi nikakvu povratnu informaciju.
Na primjer, funkcija `println` vraća `unit`.

## Funkcije

Uz podržavanje rekurzivnih definicija, Snaskell podržava i memoizaciju preko ključne riječi `memo`. Sljedeći primjer (iz `primjeri/fibonacci.snail`) naivnu rekurzivnu implementaciju računanja Fibonaccijevih brojeva svodi na O(n):

```
def memo fib(n: int) -> int as // vrati n-ti fibonaccijev br.
    if n == 1 then
        return 0;
    endif

    if n == 2 then
        return 1;
    endif

    return fib(n-1) + fib(n-2);
enddef
```

Pozivi `fib(200)` su skoro instantni jer se svode na brze upite u mape i Pythonove operacije s cijelim brojevima. Naravno to nije slučaj ako se izostavi ključna riječ `memo`.

## Unos i ispis

Ispis vrijednosti je ostvaren preko funkcija `print()` i `println()`
koje su definirane u `std/io.snail`.
Rade identično osim što `println()` na kraju prelazi u novi red.

Same funkcije su ostvarene preko interne naredbe `__print`.
Naredba `__print x;` će izvrijedniti izraz `x`,
pretvoriti ga u string koji je razumljiv korisniku,
i proslijediti ga Pythonovoj `print(..., end='')` funkciji.
Pretvaranje u korisniku razumljiv prikaz je relevantno za vrijednosti korisničkih tipova:
ne želimo da se isprinta Pythonov objekt,
nego lijepo formatirano ime konstruktora s argumentima.

Unos vrijednosti se obavlja preko funkcije `input() -> string`. Funkcija `to_int(x: string) -> int` omogućava dobivanje brojeva od unesenog stringa.

Korisnički tipovi se unose preko pomoćnih funkcija, na primjeru unošenja parova:

```
def input_pair() -> Pair<int, int> as
    print("Unesite x: ");
    let x: int = to_int(input());
    print("Unesite y: ");
    let y: int = to_int(input());
    return Pa(x, y);
enddef
```

Interno, postoje naredbe `__input x;` i `__to_int from to;` koje ovu funkcionalnost delegiraju Pythonu.
