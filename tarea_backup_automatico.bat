
            @echo off

            rem Configuración de variables
            set server=DESKTOP-FO9G4LP\SQLEXPRESS
            set user=sa
            set password=22480715
            set database=EBP
            set backup_file=H:\ween.bak rem Ruta completa con el nombre del archivo

            rem Ejecutar el comando sqlcmd para realizar la copia de seguridad
            sqlcmd -S DESKTOP-FO9G4LP\SQLEXPRESS -U sa -P 22480715 -Q "BACKUP DATABASE [EBP] TO DISK = 'H:\ween.bak'"

            rem Salir del script
            exit /b 0
        