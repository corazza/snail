# Snaskell

Naša implementacija [Snaila](https://www.cs.rpi.edu/courses/fall01/modcomp/project2.pdf) koju zovemo Snaskell je inspirirana Haskellom i proširuje Snail dodavanjem sljedećih mogućnosti:

1. korisnički tipova podataka i type checking
2. polimorfizam (templates/generics)
3. jednostavni pattern matching
4. definiranje funkcija (može rekurzivnih)

Primjer (`python snail.py ../primjeri/liste.snail` u `src/`):

```
=== typechecking ===
Nil:  List<_>
Concat:  (A, List<A>) -> List<A>
None:  Option<_>
Some:  (A) -> Option<A>
head:  (List<A>) -> Option<A>
print:  (A) -> unit
println:  (A) -> unit
input:  () -> int
unesi_element:  (int, List<A>) -> List<A>
unesi_n_elemenata_rek:  (List<A>, int) -> List<A>
unesi_n_elemenata:  (int) -> List<int>
n:  int
lista:  List<int>

=== pokretanje ===
Unesite broj elemenata: 3
Unesite element 3: 1
Unesite element 2: 2
Unesite element 1: 3
Unesena lista:
Concat(3, Concat(2, Concat(1, Nil)))
Prvi element: 3
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
data Option<A> as
    None,
    Some(A)
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

`Nil` predstavlja bazni slučaj,
a `Concat(A, List<A>)` predstavlja vrijednost tipa `A` koja je dodana na početak liste tipa `List<A>`.


## Pattern matching

Korisnički tipovi podataka u Snaskellu imaju oblik "sume produkta" tipova,
u smislu da su konstruktori članovi sume, a polja konstruktora faktori produkta.
U ovom kontekstu, suma se može shvatiti kao *ili* (`List<A>` je ili `Nil` ili `Concat`),
a produkt se može shvatiti kao *i* (`Concat(A, List<A>)` sadrži i `A` i `List<A>`).
Takva algebarska interpretacija tipova od klasične `case` sintakse iz C-ovskih jezika
daje znatno korisniju konstrukciju koja pomaže u kontroli toka,
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
`match` naredba prima neku složenu vrijednost (tj. instancu tipa koji ima konstruktore, u ovom slučaju `xs`).
Tijelo match naredbe sadrži nizove oblika *pattern => naredba*.
Pattern mora biti jedan od konstruktora tipa kojeg ima složena vrijednost `match` naredbe,
preciznije pattern je "oblik" konstruktora koji umjesto argumenata
(tj. konkretnih vrijednosti koje bi instancirale tip na kojeg se konstruktor odnosi)
sadrži slobodne varijable.
U gornjem primjeru, pattern `Concat(x, tail)` uvodi slobodne varijable `x` i `tail`.
Kažemo da se vrijednost dana matchu (`xs`) poklapa s nekim patternom ako je sastavljana od istog konstruktora na koji se odnosi pattern.
Npr. ako je dani `xs == Concat(1, Nil)`, on se poklapa s patternom `Concat(x, tail)` i ne s `Nil`.
Ako se dana vrijednost poklapa s patternom,
zvršit će se uz taj pattern vezana naredba tako da se  varijable iz patterna uvedu u scope i vežu za dijelove dane vrijednosti
(`x` će u naredbi imati vrijednost `1`, a `tail` vrijednost `Nil`).

Type checking će se pobrinuti da su pokriveni svi mogući slučajevi, i da su to samo oni koji odgovaraju tipu dane vrijednosti.
Korist takve restrikcije je da se svi *mogući* događaji moraju pokriti.
To je najbolje vidljivo na sljedećem primjeru koji pak analizira povratnu vrijednost `head` funkcije (taj `primjeri/liste.snail`):

```
print("Prvi element: ");

match head(lista) as
    None => print("nema ga"),
    Some(x) => print(x)
endmatch
```

Kad bi funkcionalnost `head`a implementirali u klasičnim programskim jezicima poput C-a ili Pythona,
ne bi mogli biti sigurni da pozivatelji provjeravaju slučaj u kojemu `head` vrati null pointer ili `None`,
ali Snaskell program u kojemu se to ne provjerava neće proći type checking.

Nažalost ovo je daleko od pune moći koju se inače očekuje od matcha,
a to je da se umjesto ovako usko definiranih patterna mogu koristiti proizvoljni izrazi,
tj. da se dopusti da istovremeno postoje patterni
`Concat(x, tail)`, `Concat(f(a), Nil)`, `Concat(x, Concat(y, Nil))` i slično.

## Type checking

Type checking se odvija statički, prije izvršavanja programa, te osigurava sljedeće.

1. Dani argumenti se poklapaju s parametrima funkcija u tipu.
2. Funkcije vraćaju vrijednost dobrog tipa (kakav je definiran).
3. Obrasci u match izrazima pokrivaju sve konstruktore, i samo konstruktore tog tipa.

Točke (1) i (2) se odnose i na konstruktore, koje možemo shvatiti kao funkcije.

println(Concat(1, Concat(2, Nil))); // OK
// println(Concat(1, Concat("asdf", Nil))); // type error!

