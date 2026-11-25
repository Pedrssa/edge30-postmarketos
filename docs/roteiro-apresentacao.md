# Roteiro da apresentação — Linux em smartphones

Falas completas na ordem da [apresentação de 12 slides](../presentation/index.html).

## Slide 1 — Abertura · Luis Eduardo

> Bom dia, pessoal. Nosso grupo é formado por Luis Eduardo Barbosa de Menezes Junior, Murilo Ribeiro de Lima, Pedro Henrique Martins Mattos Paranhos Barreiros, Ricardo Henrique da Rocha Silva e Brunno Otavyo de Jesus Aguiar.
>
> Hoje a gente vai comparar três sistemas Linux para smartphones: postmarketOS, Mobian e Ubuntu Touch. Depois, vamos mostrar o que aconteceu quando instalamos o postmarketOS em um Motorola Edge 30.

## Slide 2 — O problema · Luis Eduardo

> Um celular pode continuar funcionando mesmo depois que o fabricante para de fornecer atualizações. Foi daí que surgiu a nossa pergunta: dá pra aproveitar esse aparelho instalando um Linux parecido com o que usamos no computador? O Android já usa um kernel Linux, mas tem uma estrutura própria para aplicativos e drivers. Quando a gente troca o sistema, precisa descobrir quais recursos do celular continuam funcionando. Agora, Murilo vai explicar como esse Linux se organiza por dentro.

## Slide 3 — Como um Linux móvel funciona · Murilo

> Na base está o kernel, que conversa com o hardware. Acima dele ficam os serviços e programas que cuidam de funções como rede, telefonia e instalação de pacotes. O Wayland faz parte da camada gráfica, e o Phosh é a interface que a gente vê e usa no celular. Se faltar um driver, o sistema pode iniciar normalmente e ainda assim ficar sem uma função, como a câmera.

## Slide 4 — As três distribuições · Murilo

> Dá pra guardar assim. O postmarketOS usa Alpine e busca prolongar a vida útil dos aparelhos. O Mobian leva o Debian para o celular, com ferramentas conhecidas como o APT. E o Ubuntu Touch tem uma interface própria, chamada Lomiri, e usa o Halium em muitos aparelhos pra aproveitar componentes do Android. Agora, Pedro vai explicar como essas diferenças pesaram na nossa escolha.

## Slide 5 — Por que escolhemos o postmarketOS · Pedro Henrique

> O postmarketOS tem uma lista maior de aparelhos, com níveis de suporte diferentes. O Mobian está disponível para menos modelos. O Ubuntu Touch oferece uma experiência mais integrada nos aparelhos compatíveis. Pro nosso projeto, a escolha foi prática: entre as três opções, o postmarketOS era o que tinha uma adaptação para o Edge 30. E esse suporte ainda era experimental.

## Slide 6 — A diferença entre os kernels · Pedro Henrique

> Quando a gente fala em *mainline*, está falando do kernel mantido no projeto oficial do Linux. Integrar um celular a esse kernel exige trabalho nos drivers, mas permite acompanhar versões mais novas. Já o Halium aproveita o kernel e drivers que o fabricante disponibilizou para o Android. Isso ajuda a colocar recursos em funcionamento, mas mantém a dependência desses componentes. A gente comparou as três propostas e testou o postmarketOS no Edge 30. O Ricardo vai mostrar como foi essa parte.

## Slide 7 — O aparelho usado · Ricardo Henrique

> A gente usou um Motorola Edge 30, modelo XT2203-1, conhecido como *dubai* na documentação. Como esse aparelho estava na categoria de testes, tivemos que gerar as imagens do sistema para ele. Depois que o Linux iniciou, vimos a interface Phosh na tela e conseguimos acessar o aparelho pela rede usando SSH.

## Slide 8 — Como foi a instalação · Ricardo Henrique

> A instalação do Edge 30 teve duas etapas. Primeiro, usamos o Ubuntu em uma máquina virtual e rodamos o pmbootstrap para preparar as imagens. Depois, usamos o fastboot pelo terminal do computador para gravar essas imagens no aparelho. Com o sistema iniciado, configuramos o Wi-Fi e confirmamos o acesso remoto. A VM preparou as imagens, e o terminal do computador foi usado para gravá-las.

## Slide 9 — O que funcionou nos testes · Ricardo Henrique

> A gente auditou 34 subsistemas. Confirmamos que recursos como toque, aceleração gráfica, áudio, Wi-Fi e Bluetooth funcionaram nos testes. Também encontramos um travamento na suspensão, e as chamadas ficaram sem validação porque o aparelho estava sem chip. Agora, Brunno vai explicar o que esses resultados dizem sobre o uso do celular.

## Slide 10 — O principal problema encontrado · Brunno Otavyo

> A documentação citava relatos de baixa responsividade. No nosso aparelho, o toque registrou eventos e a GPU estava acelerando. O problema mais claro que encontramos foi na suspensão: o aparelho travava ao tentar entrar nesse estado. Isso mostra que ter suporte para um modelo ainda pode deixar pendências importantes para o dia a dia.

## Slide 11 — Resultado final · Brunno Otavyo

> No fim, o Edge 30 rodou Linux com interface gráfica, Wi-Fi e acesso por SSH. Também confirmamos recursos como toque, áudio, Bluetooth e aceleração gráfica. Já dá pra usar o aparelho como bancada de testes. Para avaliar o uso como celular no dia a dia, ainda é preciso resolver a suspensão e testar a telefonia com um chip.

## Slide 12 — A primeira tentativa e o erro · Brunno Otavyo

> Pra fechar, na nossa primeira tentativa, a gente executou os comandos direto no terminal do computador, fora da máquina virtual. O nosso erro foi seguir com o teste em um celular com a bateria estufada. A máquina virtual entrou em outra etapa, quando a gente preparou as imagens para o Edge 30. A lição foi conferir as condições físicas do aparelho antes de iniciar qualquer teste. Obrigado, pessoal.
