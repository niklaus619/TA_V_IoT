# Git-Handling

Beim Arbeiten mit Git immer zuerst den Branch auswählen, auf dem du gerade arbeitest.

0. Prüfe zuerst, auf welchem Branch du dich aktuell befindest:
   ```bash
   git branch
   ```

1. Wechsel in den gewünschten Branch:
   ```bash
   git switch <branchname>
   ```

2. Danach die aktuellen Änderungen aus dem Remote-Branch mit Rebase holen:
   ```bash
   git pull --rebase origin "branchname"
   ```

3. Nach der Bearbeitung der Anpassungen alle geänderten Dateien hinzufügen:
   ```bash
   git add .
   ```

4. Commit mit einer kurzen Beschreibung erstellen, am Ende immer mit "(xh)":
   ```bash
   git commit -m "hier deine commit aenderung mit (xh) am schluss"
   ```

5. Wenn alle Änderungen fertig sind, alles auf den Main-Branch mit Force-with-Lease pushen:
   ```bash
   git push --force-with-lease origin "branchname"
   ```

## Weitere wichtige Git-Befehle

Um einen neuen Branch zu erstellen:
```bash
git checkout -b "feature/deinBranchname"
```

Um alle Änderungen, die noch nicht gestaged und committed sind, zu verwerfen:
```bash
git restore .
```

Um einen Branch zu mergen, zuerst auf den Ziel-Branch wechseln:
```bash
git switch "Zielbranch"
```

Danach den zu mergenden Branch mergen:
```bash
git merge --no-ff "zu mergenden Branch"
```

Wichtig: Vor dem Arbeiten immer zuerst mit `git branch` prüfen, auf welchem Branch du bist. Danach die Befehle in der Konsole ausführen.
