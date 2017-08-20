# rankP
rankP

## Descrição
This project works with a database (PostgreSQL) and with the flask framework for python to create an catalog app.
The project contain a own authorization system and a third-party one (Google+).

## Resumo
O presente projeto de site/comunidade de leitores tem por objetivo avaliar o impacto de artigos cientificos por meio  de  dinâmicas  de redes sociais inspiradas no reddit e no Hack news. Os artigos seram listados de acordo com o impacto que será medido de  acordo com os upvotes e down votes dos artigos, que seram propostos para discussão pelos usuários, as discussões da comunidade do site, que seram validadas por meio desses upvotes e downvotes. O fatores de impactos serão quantificados e separados em julgamentos positivos, julgamentos negativos, comentários sobre erros, upvotes e downvotes e compartilhamentos da discussão. A partir dessa metodologia será possível dar enfase as pesquisas de impacto relativo a comunidade que os lê, de maneira a ser uma forma altenartiva de verificar a qualidade dos artigos, distribuir recursos e aproveitar o potencial da competitividade da pesquisa na faculdade.  Além disso o site é aberto e gratuito para qualquer pessoa interessada nas pesquisas discutidas, inclusive investidores. O  Banco de dados também tem potencia para medir os impactos de instituições, autores  e etc. AQUI NÃO SERAM COMPARTILHADOS OS ARTIGOS PROPIAMENTE DITOS.

## Projeto
Feito um artigo científico, como medir seu impacto? Que método de medida de impacto alternativo poderia destacar artigos de valor acadêmico legìtimo? Como expor pesquisas de qualidade que não são destacadas  apenas por meio do numero de citações referentes a pela revista onde foi publicada?
O nosso projeto tem por objetivo medir o impacto de artigos cientificos de maneira alternativa para que artigos que não são destacados com os metodos vigentes possam ser expostos. Dessa  maneira seria possível aplicar investimentos em projetos de qualidade, o que aumentaria a competitividade da pesquisa da faculdade.
O projeto  consiste num site, inspirado no reddit e no hack news, que é uma  comunidade de leitores de  artigos interessados em discutir sobre os conteudos que estão sendo publicados nas revistas. O  usuário, com uma conta nesse site de usuário especializado ou não, vai poder postar uma discussão a  respeito de  um determinado artigo, escrevendo nela informações básicas tais como o  título, os autores, o resumo devidamente referenciado e tags que permintam a busca desse artigo. Iniciada a discussão, que é separada em duas, um para o usuário especializado e  outra  para o não especializado, seram escritos comentários, a favor do artigo ou contra ele, e para eles seram associados upvotes e dowmvotes  da mesma forma que tammbém são associados aos  artigos. Além desses comentários também terá uma aba para escrever sobre erros encontrados nos artigos, que também teram upvotes e downvotes. Nessa janela também terá a opção de compartilhar essa página nas redes sociais
Da  mesma  maneira que no reddit e no hack news esses artigos serão listados por impacto e por tempo de presença no site (a opção de tempo de impacto será opcional para que os artigos sejam apresentados apenas em ordem de impacto). Esse impacto é um processamento dos downvotes e unvotes dos comentários e será dividido  em cinco quantificadores de impacto, julgamento positivo da comunidade, julamento negativo da comunidade, downvotes e upvotes do artigo, pontuação por comenários de erros e também o numero de compartilhamentos do artigo.
A listagem pode ser filtrada por meio de filtros de pesquisa para fazer um ranking dos artigos com maior impacto. 
Consequentemente, a partir dessa listagem por ordem de impacto é póssivel destacar pesquisas que foram avaliadas pela  comunidade, o que possibilita que orgão e pessoas interessadas em pesquisa de alto impacto relativo aos leitores de artigos possam encontrar. A partir disso tambem é possível ter outra base de dados para direcionar os recursos para pesquisa. Aĺém disso, aṕartir dessa base de dados, é possível tentar medir o impacto de instituições  e autores.
Essa plataforma não foi feita para ser exclusivamente acadamica, a pesquisa pode ser divulgada e vista  por  qualquer pessoa capaz de lidar com as dificuldades de ler um artigo ou que talvez já estaja acostumada.  Contudo, claramente, é necessária uma política para nortear e manter o controle das discussões para manter a verassidade dos dados.


## Whats included
 - /static
 - /templates
 - databasesetup.py
 - project.py
 - Vagrantfile
 - pg_config.sh
 
### /static
Repository where the static file such as css, javascript and images are.

### /templates
Repository to keep all the html files

### databasesetup.py
Python file that setup the catalog database

### project.py
Main file that contains all the backend code for the app

### Vagrantfile and pg_config.sh
Files to config the Virtual Machine and setup the environment

## How to setup the environment
First you have to install VirtualBox and Vagrant.
When both are installed, clone this repository, navigate to the folder and run "vagrant up" on your terminal.
With the vagrant configurated run "vagrant ssh".
then navigate to /vagrant

## How to run the App
In the /vagrant folder run the project.py file.
Go to your browser and access http://localhost:3000