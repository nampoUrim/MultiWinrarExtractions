# Archive Extractor

A lightweight Windows desktop application for extracting ZIP, RAR, and
7Z archives with WinRAR.

The application provides a simple Tkinter interface to select a folder,
process the archives found directly inside it, and monitor extraction
progress and results.

## Features

-   Detects WinRAR in its default installation location.
-   Finds `.zip`, `.rar`, and `.7z` files in the selected folder.
-   Extracts each archive into a folder with the same name as the
    archive (without its extension).
-   Skips an archive when its destination folder already exists.
-   Displays extraction progress, a percentage, activity messages, and a
    final summary.
-   Runs extraction in a worker thread so the interface remains
    responsive.

## Requirements

-   Windows

-   Python 3

-   WinRAR installed at the default path:

    `C:\Program Files\WinRAR\WinRAR.exe`

The application currently checks only this WinRAR installation path. If
WinRAR is installed elsewhere, the detection function must be updated.

## Run the application

1.  Save the Python source code in a file, for example
    `archive_extractor.py`.

2.  Open Command Prompt in the directory containing the file.

3.  Run:

    ``` cmd
    python archive_extractor.py
    ```

No third-party Python packages are required; the application uses
Python's standard library.

## How to use

1.  Launch the application.
2.  Click **Browse** and select the folder containing the archives.
3.  Click **Start Extraction**.
4.  Follow the progress bar and activity log.
5.  Review the final counts for successful, failed, and skipped
    archives.

## Extraction behavior

For an archive named `example.zip`, the application creates an output
folder named `example` beside the archive and extracts the contents
there.

The current implementation:

-   Searches only the selected folder, not its subfolders.
-   Supports files whose extensions are `.zip`, `.rar`, or `.7z`
    (case-insensitive).
-   Skips extraction if the destination folder already exists. It does
    not check whether that folder contains a complete extraction.
-   Calls WinRAR with the `x`, `-y`, and `-o-` options.
-   Does not delete or modify the original archive.

## Project structure

The project can be kept as a single Python file:

``` text
archive-extractor/
└── archive_extractor.py
```

## Troubleshooting

### WinRAR not found

Make sure WinRAR is installed at:

`C:\Program Files\WinRAR\WinRAR.exe`

If it is installed in another location, update `find_winrar()` in the
source code.

### An archive is skipped

The application skips an archive when a folder with the archive's base
name already exists beside it. Rename or move that destination folder if
you want the application to attempt extraction again.

### Extraction failed

Check that the archive can be opened by WinRAR and that you have
permission to read the archive and write to the selected folder.

## License

This project is distributed under the MIT License. See the `LICENSE`
file for details.
