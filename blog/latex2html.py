#!/usr/bin/env python3
import re
import os
import sys
import subprocess
from datetime import datetime
import tempfile
import shutil
import json
from pathlib import Path

class TufteLatexToHTML:
    def __init__(self, template_path="blog_template.html"):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_template = os.path.join(script_dir, template_path)
        
        # Read the template
        with open(default_template, 'r', encoding='utf-8') as f:
            self.template = f.read()
        
        self.temp_dir = tempfile.mkdtemp()
        
        # Define the tex4ht configuration
        self.tex4ht_config = """
                            \\Preamble{xhtml,html5,mathml,charset=utf-8,fn-in,2,sections+}

                            % Configure footnotes to be sidenotes
                            \\Configure{footnote}{<span class="numbered-sidenote"><sup class="sidenote-ref">}{</sup><span class="sidenote">}{</span></span>}

                            % Configure theorem-like environments
                            \\Configure{theorem}{<div class="theorem">}{</div>}
                            \\Configure{proof}{<div class="proof">}{</div>}
                            \\Configure{definition}{<div class="definition">}{</div>}
                            \\Configure{lemma}{<div class="lemma">}{</div>}
                            \\Configure{corollary}{<div class="corollary">}{</div>}

                            % Configure section titles
                            \\Configure{section}{}{}
                            {<h2 class="section-title">}{</h2>}
                            \\Configure{subsection}{}{}
                            {<h3 class="subsection-title">}{</h3>}

                            % Configure math for MathJax
                            \\Configure{$}{}{}
                            \\Configure{$$}{}{}
                            \\Configure{[]}{}{}
                            \\Configure{equation}{}{}

                            % Configure title and date
                            \\Configure{TITLE+}{<h1 class="blog-title">}
                            \\Configure{TITLE-}{</h1>}
                            \\Configure{AUTHOR+}{<p class="author blog-metadata">}
                            \\Configure{AUTHOR-}{</p>}
                            \\Configure{DATE+}{<p class="blog-metadata">}
                            \\Configure{DATE-}{</p>}

                            % Configure lists
                            \\Configure{itemize}
                            {<ul>}
                            {</ul>}
                            {<li>}
                            {</li>}
                            \\Configure{enumerate}
                            {<ol>}
                            {</ol>}
                            {<li>}
                            {</li>}

                            % Configure figures and tables
                            \\Configure{figure}
                            {<figure class="margin-figure">}
                            {</figure>}
                            {<figcaption>}
                            {</figcaption>}
                            \\Configure{caption}
                            {}
                            {<figcaption>}
                            {</figcaption>}
                            {}

                            % Configure references and citations
                            \\Configure{cite}
                            {<span class="citation">}
                            {</span>}
                            \\Configure{ref}
                            {<span class="ref">}
                            {</span>}

                            \\begin{document}
                            \\EndPreamble
                            """

    def __del__(self):
        """Cleanup temporary directory"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def setup_tex4ht(self, input_file):
        """Setup tex4ht configuration file and copy input file to temp directory"""
        # Copy input file to temp directory
        temp_input = os.path.join(self.temp_dir, 'input.tex')
        
        # Read and modify the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title, author, date from original content
        title_match = re.search(r'\\title\{(.*?)\}', content, re.DOTALL)
        author_match = re.search(r'\\author\{(.*?)\}', content, re.DOTALL)
        date_match = re.search(r'\\date\{(.*?)\}', content, re.DOTALL)
        
        title = title_match.group(1) if title_match else ''
        author = author_match.group(1) if author_match else ''
        date = date_match.group(1) if date_match else '\\today'
        
        # Basic preamble with essential packages
        preamble = r"""\documentclass{article}

% Basic packages
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[english]{babel}
\usepackage{amsmath,amsfonts,amsthm,amssymb}
\usepackage{mathpazo}
\usepackage{float}
\usepackage{caption}
\usepackage{stmaryrd}
\usepackage{multicol}
\usepackage{booktabs}
\usepackage{verbatim}
\usepackage{enumerate}
\usepackage{fancyhdr}
\usepackage{sectsty}
\usepackage{geometry}
\usepackage{hyperref}

% Page geometry
\geometry{left=3in,top=1in,right=1in,bottom=1in,marginparwidth=2in,marginparsep=0.5in}

% Header/footer setup
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[R]{\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\setlength{\headheight}{13.6pt}

% Section formatting
\allsectionsfont{\normalfont\bfseries}

% Theorem environments
\theoremstyle{plain}
\newtheorem{thm}{Theorem}
\newtheorem{cor}[thm]{Corollary}
\newtheorem{prop}[thm]{Proposition}
\newtheorem{facts}[thm]{Facts}
\newtheorem{fact}[thm]{Fact}
\newtheorem{clm}[thm]{Claim}
\newtheorem{lem}[thm]{Lemma}
\newtheorem{conj}[thm]{Conjecture}
\newtheorem{quest}[thm]{Question}

\theoremstyle{definition}
\newtheorem{defn}[thm]{Definition}
\newtheorem{defns}[thm]{Definitions}
\newtheorem{con}[thm]{Construction}
\newtheorem{exmp}[thm]{Example}
\newtheorem{exmps}[thm]{Examples}
\newtheorem{notn}[thm]{Notation}
\newtheorem{notns}[thm]{Notations}
\newtheorem{addm}[thm]{Addendum}
\newtheorem{exer}[thm]{Exercise}

\theoremstyle{remark}
\newtheorem{rem}[thm]{Remark}
\newtheorem{rems}[thm]{Remarks}
\newtheorem{warn}[thm]{Warning}
\newtheorem{sch}[thm]{Scholium}

% Math commands
\newcommand{\bra}[1]{\left(#1\right)}
\newcommand{\sbra}[1]{\left[#1\right]}
\newcommand{\Mod}[1]{\ (\text{mod}\ #1)}
\newcommand{\op}[1]{#1^{\text{op}}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\N}{\mathbb{N}}
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\mZ}{\mathcal{Z}}
\newcommand{\C}{\mathbb{C}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\F}{\mathbb{F}}
\newcommand{\bA}{\mathbb{A}}
\newcommand{\bH}{\mathbb{H}}
\newcommand{\one}{\mathbb{1}}
\newcommand{\mC}{\mathcal{C}}
\newcommand{\mO}{\mathcal{O}}
\newcommand{\mR}{\mathcal{R}}
\newcommand{\mS}{\mathcal{S}}
\newcommand{\lp}{{\mathfrak{p}}}
\renewcommand{\P}{\mathbb{P}}
\newcommand{\E}{\mathbb{E}}

% Math operators
\DeclareMathOperator{\dist}{dist}
\DeclareMathOperator{\aut}{Aut}
\DeclareMathOperator{\gal}{Gal}
\DeclareMathOperator{\var}{\textbf{var}}
\DeclareMathOperator{\orb}{Orb}
\DeclareMathOperator{\ff}{Frac}
\DeclareMathOperator{\stab}{Stab}
\DeclareMathOperator{\inn}{Inn}
\DeclareMathOperator{\Ind}{Ind}
\DeclareMathOperator{\Res}{Res}
\DeclareMathOperator{\spn}{Span}
\DeclareMathOperator{\out}{Out}
\DeclareMathOperator{\im}{Im}
\DeclareMathOperator{\rk}{rk}
\DeclareMathOperator{\disc}{disc}
\DeclareMathOperator{\tors}{Tors}
\DeclareMathOperator{\Mor}{Mor}
\DeclareMathOperator{\End}{End}
\DeclareMathOperator{\Hom}{Hom}
\DeclareMathOperator{\Nat}{Nat}
\DeclareMathOperator{\spec}{Spec}
\DeclareMathOperator{\ann}{Ann}
\DeclareMathOperator{\ord}{ord}
\DeclareMathOperator{\conjc}{Conj}
\DeclareMathOperator{\Br}{Br}
\DeclareMathOperator{\Tr}{Tr}
\DeclareMathOperator{\Nm}{Nm}
\DeclareMathOperator{\Char}{char}

% Allow display breaks
\allowdisplaybreaks

% Title information
\title{""" + title + r"""}
\author{""" + author + r"""}
\date{""" + date + r"""}
"""

        # Extract document content
        doc_match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', content, re.DOTALL)
        if doc_match:
            document_content = doc_match.group(1)
            # Remove tikz environments
            document_content = re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', '', document_content, flags=re.DOTALL)
            # Remove other problematic environments
            document_content = re.sub(r'\\begin\{tcolorbox\}.*?\\end\{tcolorbox\}', '', document_content, flags=re.DOTALL)
            # Remove Hebrew text commands
            document_content = re.sub(r'\\texthebrew\{.*?\}', '', document_content, flags=re.DOTALL)
            # Create new content
            content = preamble + "\n\\begin{document}\n\\maketitle\n" + document_content + "\n\\end{document}"
        
        # Write modified content
        with open(temp_input, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Create tex4ht config file
        config_path = os.path.join(self.temp_dir, 'config.cfg')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(r"""
\Preamble{xhtml,mathml,charset=utf-8,-css}
\Configure{VERSION}{}
\Configure{DOCTYPE}{\HCode{<!DOCTYPE html>\Hnewline}}
\Configure{HTML}{\HCode{<html lang="en">\Hnewline}}{\HCode{\Hnewline</html>}}
\Configure{@HEAD}{}
\Configure{@HEAD}{\HCode{<meta charset="UTF-8" />\Hnewline}}
\Configure{@HEAD}{\HCode{<meta name="generator" content="TeX4ht" />\Hnewline}}
\Configure{@HEAD}{\HCode{<meta name="viewport" content="width=device-width,initial-scale=1" />\Hnewline}}
\begin{document}
\EndPreamble
""")
        return temp_input, config_path

    def run_tex4ht(self, input_file):
        """Run tex4ht conversion using MiKTeX on Windows"""
        temp_input, config_path = self.setup_tex4ht(input_file)
        print(f"\nProcessing {input_file}...")
        print(f"Temporary directory: {self.temp_dir}")
        
        try:
            # First compile with latex
            print("\nRunning initial LaTeX compilation...")
            latex_cmd = [
                'latex',
                '-interaction=nonstopmode',
                f'-output-directory={self.temp_dir}',
                temp_input
            ]
            
            print(f"LaTeX command: {' '.join(latex_cmd)}")
            try:
                result = subprocess.run(latex_cmd,
                                   capture_output=True,
                                   text=True,
                                   timeout=120)
            except subprocess.TimeoutExpired:
                # Read the log file to see what happened
                log_file = os.path.join(self.temp_dir, 'input.log')
                if os.path.exists(log_file):
                    print("\nLaTeX compilation timed out. Checking log file:")
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                        # Print the last few lines of the log
                        last_lines = log_content.split('\n')[-20:]
                        print('\n'.join(last_lines))
                raise Exception("LaTeX compilation timed out - the document might be too complex or there might be an error")
            
            if result.returncode != 0:
                # Read the log file for detailed error information
                log_file = os.path.join(self.temp_dir, 'input.log')
                if os.path.exists(log_file):
                    print("\nLaTeX compilation failed. Checking log file:")
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                        # Look for error messages
                        error_lines = [line for line in log_content.split('\n') 
                                     if line.startswith('!') or 'Error:' in line]
                        if error_lines:
                            print("\nFound the following LaTeX errors:")
                            for line in error_lines:
                                print(line)
                return None
            
            print("LaTeX compilation successful")
            
            # Change to temp directory for tex4ht
            os.chdir(self.temp_dir)
            
            # Run tex4ht chain
            commands = [
                ['tex4ht', 'input.tex', '-cunihtf'],
                ['t4ht', 'input.tex', '-d./', '-cunihtf'],
            ]
            
            for cmd in commands:
                print(f"\nRunning command: {' '.join(cmd)}")
                try:
                    result = subprocess.run(cmd,
                                       capture_output=True,
                                       text=True,
                                       timeout=60)
                    if result.returncode != 0:
                        print(f"Warning: Command failed:")
                        print(result.stderr)
                        print("\nCommand output:")
                        print(result.stdout)
                except Exception as e:
                    print(f"Error running command: {str(e)}")
                    print("\nCommand output:")
                    if hasattr(e, 'output'):
                        print(e.output)
            
            # Check for output file
            output_html = os.path.join(self.temp_dir, 'input.html')
            if os.path.exists(output_html):
                print(f"\nSuccessfully generated HTML in {output_html}")
                with open(output_html, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                print("\nFiles in temporary directory:")
                for file in os.listdir(self.temp_dir):
                    print(f"  - {file}")
                    # If the file is a log file, print its contents
                    if file.endswith('.log'):
                        print(f"\nContents of {file}:")
                        with open(os.path.join(self.temp_dir, file), 'r', encoding='utf-8') as f:
                            print(f.read())
                raise Exception("Failed to generate HTML output")
                
        except Exception as e:
            print(f"\nError during conversion: {str(e)}")
            print("\nFiles in temporary directory:")
            for file in os.listdir(self.temp_dir):
                print(f"  - {file}")
                # If the file is a log file, print its contents
                if file.endswith('.log'):
                    print(f"\nContents of {file}:")
                    with open(os.path.join(self.temp_dir, file), 'r', encoding='utf-8') as f:
                        print(f.read())
            return None

    def post_process_html(self, html):
        """Post-process the HTML to improve output quality"""
        # Fix equation numbers
        html = re.sub(r'<span class="eqno">\(([\d.]+)\)</span>', 
                     r'<span class="equation-number">(\1)</span>', html)
        
        # Fix figure positioning
        html = re.sub(r'<figure(.*?)>(.*?)<img(.*?)>(.*?)</figure>', 
                     r'<figure\1 style="text-align: center;">\2<img\3>\4</figure>', html)
        
        # Fix table styling
        html = re.sub(r'<table>', 
                     r'<table class="table">', html)
        
        # Fix links
        html = re.sub(r'<a href="([^"]+)">', 
                     r'<a href="\1" target="_blank">', html)
        
        # Clean up unnecessary divs
        html = re.sub(r'<div class="maketitle">.*?</div>', '', html, flags=re.DOTALL)
        html = re.sub(r'<div class="tableofcontents">.*?</div>', '', html, flags=re.DOTALL)
        html = re.sub(r'<div class="crosslinks">.*?</div>', '', html, flags=re.DOTALL)
        
        return html

    def extract_metadata(self, tex4ht_html):
        """Extract title and date from tex4ht output"""
        # Try to find title
        title_match = re.search(r'<h1 class="blog-title">(.*?)</h1>', tex4ht_html, re.DOTALL)
        if not title_match:
            title_match = re.search(r'<title>(.*?)</title>', tex4ht_html, re.DOTALL)
        title = title_match.group(1) if title_match else "Untitled"
        
        # Try to find date
        date_match = re.search(r'<p class="blog-metadata">(.*?)</p>', tex4ht_html, re.DOTALL)
        date = date_match.group(1) if date_match else datetime.now().strftime("%B %d, %Y")
        
        return title, date

    def extract_body(self, tex4ht_html):
        """Extract the main content from tex4ht output"""
        # Try to find the main content
        body_match = re.search(r'<body[^>]*>(.*?)</body>', tex4ht_html, re.DOTALL)
        if body_match:
            body = body_match.group(1)
            # Post-process the body
            body = self.post_process_html(body)
            return body
        return tex4ht_html

    def convert(self, input_file):
        """Convert LaTeX content to HTML using tex4ht and apply blog template"""
        # Run tex4ht conversion
        tex4ht_html = self.run_tex4ht(input_file)
        if not tex4ht_html:
            raise Exception("Conversion failed")
        
        # Extract metadata and content
        title, date = self.extract_metadata(tex4ht_html)
        body = self.extract_body(tex4ht_html)
        
        # Replace template placeholders
        html = self.template.replace('Title of Your Blog Post', title)
        html = html.replace('January 15, 2024', date)
        
        # Replace the example content with the converted content
        article_start = html.find('<article class="blog-container">')
        article_end = html.find('</article>')
        
        if article_start != -1 and article_end != -1:
            html = (html[:article_start] + 
                   '<article class="blog-container">\n' +
                   body + '\n' +
                   '</article>' +
                   html[article_end + 10:])
        
        return html

def check_miktex_installation():
    """Check if MiKTeX and required tools are installed"""
    required_tools = ['latex', 'tex4ht', 't4ht']
    missing_tools = []
    
    print("\nChecking required tools:")
    for tool in required_tools:
        try:
            if tool == 'latex':
                cmd = ['latex', '--version']
            else:
                cmd = [tool, '-v']
                
            result = subprocess.run(cmd,
                                 capture_output=True,
                                 text=True,
                                 timeout=10)
            print(f"  - {tool}: Found")
            if result.stdout:
                first_line = result.stdout.splitlines()[0]
                print(f"    Version info: {first_line}")
        except subprocess.TimeoutExpired:
            print(f"  - {tool}: Command timed out")
            missing_tools.append(tool)
        except FileNotFoundError:
            print(f"  - {tool}: Not found")
            missing_tools.append(tool)
        except Exception as e:
            print(f"  - {tool}: Error checking ({str(e)})")
            missing_tools.append(tool)
    
    if missing_tools:
        print("\nError: The following required tools are missing:")
        for tool in missing_tools:
            print(f"  - {tool}")
        print("\nPlease install the required packages in MiKTeX:")
        print("1. Open MiKTeX Console")
        print("2. Go to Packages")
        print("3. Search for and install:")
        print("   - tex4ht")
        print("   - make4ht")
        return False
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python latex2html.py input.tex")
        sys.exit(1)
    
    # Get absolute paths
    input_file = os.path.abspath(sys.argv[1])
    if not input_file.endswith('.tex'):
        print("Error: Input file must be a .tex file")
        sys.exit(1)
    
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    print(f"\nStarting LaTeX to HTML conversion process...")
    print(f"Input file: {input_file}")
    print(f"Current working directory: {os.getcwd()}")
    
    if not check_miktex_installation():
        sys.exit(1)
    
    # Create output file in same directory as input
    output_file = os.path.splitext(input_file)[0] + '.html'
    print(f"Output will be written to: {output_file}")
    
    try:
        # Convert
        print("\nInitializing converter...")
        converter = TufteLatexToHTML()
        print(f"Using temporary directory: {converter.temp_dir}")
        
        print("\nStarting LaTeX conversion process...")
        html_content = converter.convert(input_file)
        
        if html_content:
            # Write output file
            print(f"\nWriting output to {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"\nSuccessfully converted {input_file} to {output_file}")
        else:
            print("\nError: Conversion failed - no HTML content generated")
            print("Please check the LaTeX compilation and conversion logs above for errors")
            sys.exit(1)
        
    except Exception as e:
        print(f"\nError during conversion: {str(e)}")
        print("\nStack trace:")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
