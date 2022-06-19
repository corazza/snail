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

## Type checking

Type checking se odvija statički, prije izvršavanja programa, te osigurava sljedeće.

1. Da se dani argumenti poklapaju s parametrima funkcija u tipu.
2. Da funkcije vraćaju tip dobre vrijednosti (kakav je definiran).
3. 


println(Concat(1, Concat(2, Nil))); // OK
// println(Concat(1, Concat("asdf", Nil))); // type error!

