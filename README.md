# snail

Naša implementacija je inspirirana Haskellom i proširuje [Snail](https://www.cs.rpi.edu/courses/fall01/modcomp/project2.pdf) dodavanjem sljedećih mogućnosti:

- korisnički tipova podataka i type checking
- polimorfizam (templates/generics)
- elementarni pattern matching
- definiranje funkcija (može rekurzivnih)

Primjer:

```bash
cd src
python snail.py ../primjeri/liste.snail
```

U outputu se mogu vidjeti informacije o tipovima varijabli i funkcija:

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

Naravno dodatne mogućnosti naše implementacije su ograničene u usporedbi s pravim sustavima:

1. (Skoro) sve oznake tipova se moraju eksplicitno pisati, dok se u Hindley–Milner sistemu (kojeg Haskell proširuje) ne mora nijedna.
2. Varijable tipova, koje ostvaruju polimorfizam, ne mogu se restringirati (type classes u Haskellu dodaju tu mogućnost).
3. Kod pattern matchinga, obrasci ne mogu biti proizovoljne vrijednosti (dobrog tipa), već samo konstruktori koji eksplicitno navode slobodne varijable.
