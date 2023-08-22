
import subprocess

from pathlib import Path

from lib_not_dr.nuitka.compile import CompilerHelper

def gen_compiler() -> CompilerHelper:
    comp = CompilerHelper(
        output_path=Path('build'),
        src_file=Path('main/main.py'),
        
        use_lto=False,
        use_clang=True,
        use_msvc=True,
        use_mingw=False,
        enable_console=True,
        standalone=True,
        
        show_progress=True,
        show_memory=False,
        use_ccache=True,
        remove_output=True,
        
        enable_plugin=['pyqt5'],
    )
    return comp

if __name__ == '__main__':
    compiler = gen_compiler()
    
    print(compiler.as_markdown())
    
    subprocess.run(compiler.gen_subprocess_cmd())    
