#### Guia para crear una rama y mantenerla actualizada con la rama develop

1. git checkout develop
2. git pull origin develop
3. git branch --track <nombre_rama> origin/develop
4. git checkout <nombre_rama>

Cuando ya esté el commit listo en la rama donde estás trabajando, antes de subir los cambios
a la branch remota, ejecutar:

git checkout <nombre_rama>
git pull --rebase

Luego subir los cambios con:

git push origin <nombre_rama>

Cuando esté la rama de la feature subida, entrar a github y crear la Merge Request.

Comandos útiles:

- git status (ver cambios staged y unstaged)
- git log (ver historial de commits)
- git diff (ver cambios que están staged, está bueno usarlo antes de commitear para
  asegurarse que el código cambiado está bien)
- git reset --soft HEAD~1 (eliminar último commit y dejar los cambios unstaged)
- git reset --hard HEAD~1 (eliminar último commit y todos los cambios que se hicieron en el mismo)

Recomendaciones:

- Cada vez que te pongas a trabajar en tu branch, ejecutar:

git pull --rebase

Para traer siempre los últimos cambios que están en la rama que trackea tu rama local,
(develop) en este caso va a ser la mayoría de veces.

- Formato de branchs: unity/#id_descripcion
