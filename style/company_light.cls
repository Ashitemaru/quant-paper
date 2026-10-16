% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Company Template 1: Light brand background (derived from logo color #E3AA79)
% Based on fairmeta.cls
% Compilation: pdflatex --shell-escape (required for SVG logo via Inkscape)
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{company_light}
\LoadClassWithOptions{article}

% Layout %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage[top=2.25cm, bottom=2.5cm, left=2.5cm, right=2.5cm, columnsep=0.65cm]{geometry}
\RequirePackage{microtype}
\RequirePackage{placeins}
\RequirePackage{hyphenat}
\RequirePackage{setspace}
\RequirePackage{parskip}
\RequirePackage[latin, english]{babel}
\RequirePackage{lipsum}
\RequirePackage{etoolbox}

\DisableLigatures[f]{family=sf*}

% Graphics %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{graphicx}
\RequirePackage{subcaption}
% Logo is pre-converted to assets/logo.pdf via cairosvg.

% Tables %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{booktabs}
\RequirePackage{nicematrix}
\RequirePackage{multirow}
\RequirePackage{bm}
\newcommand{\nm}[1]{#1}

% Brand colors — derived from logo primary #E3AA79 (RGB 227 170 121) %%%%%%%%%%
%
%   brandbg      = 15% primary + 85% white  →  #FBF2EA  (abstract / title bg)
%   brandprimary = logo color itself         →  #E3AA79  (decorative accents)
%   brandaccent  = darkened for readability  →  #B8722E  (links, section heads)
%   brandfg      = dark neutral              →  #1C2B33  (body text)
%
\RequirePackage{xcolor}
\RequirePackage[most]{tcolorbox}
\definecolor{brandbg}{HTML}{FBF2EA}
\definecolor{brandprimary}{HTML}{E3AA79}
\definecolor{brandaccent}{HTML}{B8722E}
\definecolor{brandfg}{HTML}{1C2B33}

% References %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{hyperref}
\RequirePackage[noabbrev,nameinlink]{cleveref}
\hypersetup{
  colorlinks,
  linkcolor=brandaccent,
  citecolor=brandaccent,
  urlcolor=brandaccent
}

\RequirePackage{natbib}
\def\bibfont{\small}

% Section and caption format %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{titlesec}
\titleformat*{\paragraph}{\itshape}
\titleformat*{\section}{\Large\sffamily\bfseries\color{brandaccent}}
\titleformat*{\subsection}{\large\sffamily\bfseries}
\titleformat*{\subsubsection}{\normalsize\sffamily\bfseries}
\DeclareTextFontCommand{\textbf}{\bfseries\sffamily}

\RequirePackage{caption}
\DeclareCaptionLabelSeparator{custom}{}
\DeclareCaptionFormat{custom}{{\sffamily\textbf{#1 #2}} #3}
\captionsetup{singlelinecheck=false,format=custom,labelsep=custom,font=small}
\captionsetup[sub]{singlelinecheck=true,format=custom,labelsep=custom,font=small}

% % Custom fonts %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% \renewcommand*\ttdefault{cmvtt}
% \RequirePackage[T1]{fontenc}

% \DeclareFontFamily{T1}{optimistic}{}
% \DeclareFontShape{T1}{optimistic}{m}{n}{<-> s * [0.88] assets/optimistic}{}
% \DeclareFontShape{T1}{optimistic}{b}{n}{<-> s * [0.88] assets/optimistic}{}
% \pdfmapline{+optimistic < assets/Optimistic.ttf <T1-WGL4.enc}
% \renewcommand{\sfdefault}{optimistic}



% Custom fonts %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\renewcommand*\ttdefault{cmvtt}
\RequirePackage[T1]{fontenc}

% Commented out due to arXiv font restrictions:
%\DeclareFontFamily{T1}{optimistic}{}
%\DeclareFontShape{T1}{optimistic}{m}{n}{<-> s * [0.88] assets/optimistic}{}
%\DeclareFontShape{T1}{optimistic}{b}{n}{<-> s * [0.88] assets/optimistic}{}
%\pdfmapline{+optimistic < assets/Optimistic.ttf <T1-WGL4.enc}
%\renewcommand{\sfdefault}{optimistic}

% Fallback to arXiv-compatible sans-serif font (Helvetica or Latin Modern Sans):
\renewcommand{\sfdefault}{phv} % Helvetica (clean, widely available on arXiv)
%\renewcommand{\sfdefault}{lmss} % Alternative: Latin Modern Sans



% Authors, affiliations, metadata %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\renewcommand\addtolist[5][]{
  \begingroup
    \if\relax#3\relax\def\sep{}\else\def\sep{#5}\fi
    \let\protect\@unexpandable@protect
    \xdef#3{\expandafter{#3}\sep #4[#1]{#2}}%
  \endgroup
}

\newcommand\authorlist{}
\newcommand\authorformat[2][]{{\sffamily \bfseries #2$^{#1}$}}
\renewcommand\author[2][]{\addtolist[#1]{#2}{\authorlist}{\authorformat}{, }}

\newcommand\affiliationlist{}
\newcommand\affiliationformat[2][]{{\normalsize $^{#1}$#2}}
\newcommand\affiliation[2][]{\addtolist[#1]{#2}{\affiliationlist}{\affiliationformat}{, }}

\newcommand\contributionlist{}
\newcommand\contributionformat[2][]{{\small $^{#1}$#2}}
\newcommand\contribution[2][]{\addtolist[#1]{#2}{\contributionlist}{\contributionformat}{, }}

\newcommand\metadatalist{}
\newcommand\metadataformat[2][]{{\small {\sffamily \bfseries #1:} #2}}
\newcommand\metadata[2][]{\addtolist[#1]{#2}{\metadatalist}{\metadataformat}{\par}}

\renewcommand{\abstract}[1]{\def\abstractlist{{\color{brandfg} #1}}}
\newcommand{\email}[1]{\href{mailto:#1}{\texttt{#1}}}

\renewcommand\date[1]{\metadata[Date]{#1}}
\newcommand\correspondence[1]{\metadata[Correspondence]{#1}}

\renewcommand{\title}[1]{\newcommand{\titlelist}{{\huge\sffamily\bfseries #1}}}

\newcommand{\beginappendix}{\appendix{\huge\sffamily Appendix\par}}

% Titlebox %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The entire header box (title + authors + abstract + metadata) uses brandbg
% as background — a warm, slightly tinted version of the logo color.

\newcommand{\mymaketitle}{%
  \tcbset{enhanced, frame hidden}
  \tcbset{left=0.5cm}
  \tcbset{right=0.5cm}
  \tcbset{top=0.5cm}
  \tcbset{bottom=0.5cm}
  \tcbset{arc=10pt}
  \tcbset{colback=brandbg}
  \tcbset{before skip=0pt}
  \tcbset{grow to left by=1.5pt}
  \tcbset{grow to right by=1.5pt}
  \tcbset{overlay={\node[
    anchor=south east,
    at= (frame.south east),
    xshift=-0.5cm,
    yshift=0.5cm] {\includegraphics[width=1.5cm]{assets/logo.pdf}};}}
  %
  \begin{tcolorbox}
    \setlength{\parindent}{0cm}
    \setlength{\parskip}{0.5cm}
    {
      \setlength{\parskip}{0cm}
      \raggedright
      \nohyphens
      %
      {
        \setstretch{1.618}
        \titlelist\par
      }
      \vskip 0.2cm
      %
      \authorlist\par
      \vskip 0.2cm
      %
      \affiliationlist\par
      %
      \contributionlist\par
    }
    %
    \abstractlist\par
    %
    \vskip 0.5cm
    %
    {
      \setlength{\parskip}{0cm}
      \ifdefempty{\metadatalist}{\vspace*{0.65cm}}{\metadatalist\par}
    }
  \end{tcolorbox}
  \tcbset{reset}
  \FloatBarrier
}

\if@twocolumn%
\renewcommand{\maketitle}{
\twocolumn[%
  \mymaketitle
  \vskip 0.38cm
]
}%
\else%
\renewcommand{\maketitle}{
  \mymaketitle
}%
\fi
