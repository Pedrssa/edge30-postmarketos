# Roteiro da apresentação — falas completas

14 slides · ~9–11 min de fala · 16:9. As falas estão prontas para ensaio (não são tópicos a improvisar).
Tempo estimado por slide entre colchetes. Total ≈ **10 min**.

---

## Slide 1 — Abertura · *De Android a Linux de bolso* [00:40]

> "Boa tarde. O que eu vou mostrar aqui é um projeto de engenharia embarcada: pegamos um celular
> Android comum, um **Motorola Edge 30**, e o transformamos num computador **Linux ARM64 de verdade**,
> rodando **postmarketOS**. Não é emulação, não é um app: é o sistema operacional do aparelho trocado
> na raiz. Vou contar o que a gente queria, como fizemos, o que funcionou — e, com honestidade, o que
> ainda não testamos."

---

## Slide 2 — O desafio e a motivação [00:45]

> "A motivação é simples: um celular é um computador ARM64 poderoso que a gente praticamente aluga do
> fabricante. A proposta foi tomar posse desse hardware — virar dono do sistema — e usá-lo como
> estação portátil de engenharia e redes. O desafio é que isso exige destravar o aparelho, trocar o
> sistema por completo e aceitar que, se der errado, o celular vira um peso de papel. Então todo o
> trabalho foi feito com rede de segurança: integridade conferida e um caminho de volta para o Android."

---

## Slide 3 — O que é postmarketOS (agora Nura) [00:50]

> "postmarketOS é um Linux de verdade para celulares, baseado no **Alpine Linux**. A ideia dele é dar
> vida longa a aparelhos, rodando um kernel próximo do **mainline** em vez do kernel travado de fábrica.
> Um detalhe de contexto: em setembro de 2026 o projeto foi **rebatizado para Nura** — mudou o nome e o
> domínio, mas é o mesmo projeto. Por isso, no nosso aparelho, aparece como 'Nura Linux edge'. A
> interface gráfica que usamos é a **Phosh**, feita para telas de toque."

---

## Slide 4 — Nosso dispositivo: `dubai` [00:55]

> "O aparelho é o Edge 30, variante XT2203-1, codinome **dubai**, com chip Snapdragon 778G+. Duas
> particularidades pesaram no projeto. Primeiro: no postmarketOS esse aparelho é categoria **testing** e
> **não tem imagem pronta para baixar** — ou seja, a gente *precisava construir* o sistema. Segundo: o
> kernel desse aparelho é da linha **sc7280 mainline**, e a própria wiki alerta para possível **baixa
> responsividade**. Guardei isso como risco conhecido — e sendo honesto, não medi esse impacto no nosso aparelho."

---

## Slide 5 — Objetivo e critérios de sucesso [00:40]

> "O critério de sucesso que eu estabeleci foi concreto: o aparelho tinha que **dar boot em Linux**,
> subir a **interface gráfica**, **conectar no Wi-Fi** e aceitar **acesso remoto por SSH**. Se esses
> quatro pontos estivessem de pé, o port estaria provado como base utilizável. Tudo além disso —
> áudio, câmera, chamadas — seria bônus a validar depois."

---

## Slide 6 — Ambiente e ferramentas [00:50]

> "Para construir o sistema, montei uma **máquina virtual Ubuntu**, com 4 GB de RAM, e usei o
> **pmbootstrap** — a ferramenta oficial do postmarketOS que compila o rootfs e o kernel para o
> aparelho-alvo. Do lado do Windows, usei o **fastboot** do Android platform-tools para gravar as
> partições. Então são dois mundos: a VM que *fabrica* as imagens, e o PC que as *grava* no celular."

---

## Slide 7 — Arquitetura e fluxo de boot [01:00]

> "Esse é o coração técnico. Na esquerda, a VM com o pmbootstrap gera três artefatos: o **boot.img**,
> que leva o kernel e o initramfs; o **dtbo.img**, o overlay de árvore de dispositivo, que diz ao
> kernel como é o hardware; e o **rootfs**, o sistema de arquivos inteiro, com 2 gigabytes. Esses três
> vão por fastboot para as partições boot, dtbo e userdata. No boot, o kernel sc7280 sobe, monta o
> rootfs Alpine, inicia a Phosh, e aí o Wi-Fi sobe e o SSH abre. É esse caminho que a animação está
> percorrendo agora."

---

## Slide 8 — Etapas realizadas [01:00]

> "Na prática, a sequência foi: pesquisa de viabilidade; build do sistema na VM; destravamento do
> bootloader; gravação das partições; primeiro boot; e, por fim, conexão de Wi-Fi e SSH. Faço aqui uma
> ressalva importante de honestidade: eu tenho a prova de que o sistema **funcionou** — o aparelho
> respondeu por SSH e me mandou uma captura da tela. Mas o **registro do momento exato da gravação**
> não ficou salvo; esse passo foi reconstruído a partir do fluxo oficial e dos artefatos. Está marcado
> como 'reconstruído' em todo o material."

---

## Slide 9 — Dificuldades e diagnóstico [00:50]

> "Nem tudo foi liso. O aparelho não tinha imagem pronta — resolvido construindo. Um bloco grande de
> comando não passou pelo shell do Windows e não enviou nada — resolvido mandando a árvore por um
> script via SFTP. Teve um erro de codificação de caractere ao gerar texto com sinais especiais —
> resolvido forçando UTF-8. E, mais tarde, a reconexão falhou porque o IP do aparelho mudou de rede —
> resolvido pegando o IP novo direto no celular. São problemas reais de quem opera, não de slide."

---

## Slide 10 — Evidências e como as classifico [00:50]

> "Eu não quero que vocês acreditem na minha palavra; quero mostrar a régua. Cada afirmação do projeto
> está marcada: **confirmado**, quando eu verifiquei em arquivo ou transcrição; **relatado**, quando
> foi dito mas não reconfirmei; **reconstruído**, quando infiro do fluxo; e **ausente**, quando não há
> evidência. Por exemplo: as imagens e seus hashes são confirmados; a versão do kernel é relatada; a
> gravação é reconstruída; e áudio e câmera são ausentes. Tudo isso está numa tabela de rastreabilidade."

---

## Slide 11 — Resultados [00:45]

> "O resultado central: o Edge 30 **inicializa em postmarketOS** com interface gráfica, **Wi-Fi** e
> **SSH** funcionando. Além disso, o gerenciador de pacotes opera e eu consegui instalar um conjunto de
> ferramentas de rede e **reverter tudo**, voltando o sistema idêntico ao backup. Ou seja: não é só que
> ligou — é uma base sobre a qual dá para trabalhar e experimentar com segurança."

---

## Slide 12 — Linha do tempo [00:40]

> "Em linha do tempo: no fim de outubro, a pesquisa de viabilidade. No dia 4 de novembro, o build do
> sistema e a geração das imagens — a data dos arquivos confirma isso. Ainda no dia 4, à noite, o
> aparelho já estava em Linux e respondendo. Nas semanas seguintes, operação e ajustes. E hoje, a
> documentação completa que vocês estão vendo."

---

## Slide 13 — Matriz de funcionalidades: o que testamos [00:50]

> "Aqui está a parte mais honesta do trabalho. Em verde, o que está **comprovado**: boot, interface
> gráfica, Wi-Fi, SSH e gerenciamento de pacotes. Em cinza, o que **não foi testado**: áudio, modem e
> chamadas, dados móveis, GPU, câmera, Bluetooth, NFC, sensores e bateria. Eu faço questão de não
> pintar de verde o que não medi. Isso não é fraqueza do projeto; é o próximo passo dele."

---

## Slide 14 — Aprendizados e próximos passos [00:45]

> "O aprendizado maior: dá para ter um Linux de propósito geral no bolso, mas o preço é rigor — build
> próprio, integridade conferida e caminho de volta. Os próximos passos são claros: levantar a matriz
> de funcionalidades direto no aparelho, confirmar a versão do kernel por leitura, e capturar um log
> limpo da regravação. Com isso, as partes 'reconstruídas' viram 'confirmadas'. Obrigado — o
> repositório tem o relatório completo, as evidências e esta apresentação. Perguntas?"

---

### Checagem de tempo
Soma dos blocos ≈ **10 min 03 s**. Para uma versão de 5 minutos, concentre em 1, 4, 7, 11 e 13.

---

## Slides 13–16 — acrescentados após a auditoria de 24/11/2026

> O deck passou de 14 para **17 slides**. Os quatro abaixo substituem a antiga matriz "não testado"
> e cobrem as exigências do Tema 10 (comparativo entre distros + explicação da stack).

### Slide 13 — Matriz real (≈ 2 min)

"Em 24 de novembro voltamos ao aparelho e medimos. Trinta e quatro subsistemas, um por um, cada um
com evidência de comando. Quatorze funcionam: CPU, GPU com aceleração comprovada, tela, **toque**,
Wi-Fi 6, Bluetooth, áudio, microfone, bateria. Quatro são parciais. Seis estão detectados mas não
validados — e essa distinção importa: existir em `/sys` não é funcionar. Seis não têm driver ou
falharam.

Compatibilidade: 55%. E o número vem com a conta aberta — pesos, numerador e denominador, no
relatório. Teste que não fizemos nunca entra como aprovado."

### Slide 14 — O que a medição corrigiu (≈ 2 min)

"Medir derrubou coisas que a gente achava que sabia.

Primeiro: não é postmarketOS puro — é Nura, um derivado. E o init é systemd, não OpenRC. Todo
comando `rc-status` que planejamos usar simplesmente não se aplica.

Segundo: o modem não está quebrado. Ele reporta `failed`, mas o motivo é `sim-missing` — não tem
chip. O firmware carregou, a pilha QMI funciona, ele anuncia suporte a 5G.

Terceiro, e esse é sobre nós: classificamos o touchscreen como falha crítica. Estava errado. A gente
media a contagem de interrupções por 30 segundos pedindo que tocassem a tela — mas quem ia tocar
estava lendo a instrução no computador. Interpretamos ausência de estímulo como defeito de hardware.
O teste certo capturou 6942 eventos de toque. Esse erro sozinho mudava nossa nota final de nível 2
para nível 3.

Quarto: achamos um defeito que não está na wiki oficial — a suspensão trava o aparelho."

### Slide 15 — A stack (≈ 2,5 min)

"Para entender o que é um Linux móvel, vale olhar as camadas.

Embaixo, o kernel — e aqui está a diferença que importa. O Android usa um kernel congelado pelo
fabricante. A gente usa mainline: 7.2.9, da família sc7280. É o que dá vida longa ao aparelho. Em
ARM não existe ACPI, então o hardware é descrito num Device Tree — portar um celular é, em boa
parte, escrever esse arquivo.

Acima, Alpine Linux com `apk` e systemd. Depois Wayland, que substituiu o X11 — o compositor Phoc
fala direto com o DRM e submete à GPU pelo Mesa. No topo, o Phosh, que adapta o GNOME para uma tela
de 6,5 polegadas.

E do lado, a telefonia: o modem é um computador separado, com firmware próprio, que conversa por QMI
sobre QRTR. O ModemManager traduz isso para o sistema."

### Slide 16 — Comparativo das três distribuições (≈ 3 min)

"O tema pedia comparar três caminhos.

**Ubuntu Touch** tem a melhor experiência de uso e telefonia mais madura. Mas usa Halium — uma camada
que reaproveita o kernel e os drivers Android do fabricante. Funciona rápido em muitos aparelhos, e
herda exatamente o problema que a gente queria resolver: o kernel congelado.

**Mobian** é a mais estável, baseada em Debian. Mas foca em hardware feito para Linux, tipo
PinePhone. Poucos aparelhos.

**postmarketOS** aposta em kernel mainline e alcance: mais de 300 dispositivos, a maioria em estágio
`testing`. Mais trabalho por aparelho, maturidade desigual.

Para nós a escolha foi imposta pela realidade: **era a única das três com port do Edge 30**. E é
honesto dizer que a comparação é parcial — nenhuma das outras duas roda neste aparelho, então
comparamos projetos, não três sistemas no mesmo hardware."

### Slide 17 — Encerramento (≈ 1,5 min)

"Linux no bolso dá. O preço é rigor.

O aparelho é uma estação Linux portátil: nível 3 de 5. Funciona como computador. Não funciona ainda
como substituto de celular — a suspensão trava, e câmera frontal, NFC, vibração e biometria não têm
driver.

E o gargalo não é o processador. O Snapdragon é bem suportado upstream. O gargalo são os
periféricos, que dependem de drivers escritos por voluntários e ainda não mesclados.

Fica o aprendizado que mais nos marcou: a gente errou duas vezes na auditoria, e as duas vezes foi
raciocínio sobre evidência — não execução de comando. A segunda só foi descoberta porque um
integrante do grupo discordou do resultado, baseado em usar o aparelho todo dia."

---

# ⚠️ REESTRUTURAÇÃO — deck reorganizado para o Tema 10

O deck foi reordenado: **a comparação entre distribuições virou o corpo principal** (é o tema), e o
port do Edge 30 passou a ser o **estudo de caso**, no segundo bloco.

## Nova ordem — 18 slides

**BLOCO 1 · O TEMA (slides 1–9, ~10 min)**

| # | Slide |
|---|---|
| 1 | Capa |
| 2 | O celular é um computador que a gente aluga |
| 3 | **Android é Linux — mas não é um Linux** (Bionic/ART/HAL × glibc/Wayland/systemd) |
| 4 | A stack em camadas (kernel · userspace · Wayland · shell · telefonia) |
| 5 | **postmarketOS** |
| 6 | **Mobian** |
| 7 | **Ubuntu Touch** |
| 8 | **Comparativo lado a lado** (tabela de 8 critérios) |
| 9 | **A divisão que importa: mainline × Halium** + quando usar cada um |

**TRANSIÇÃO (slide 10)** — "Comparar é fácil. Instalar é que mostra."

**BLOCO 2 · ESTUDO DE CASO (slides 11–18, ~10 min)**

| # | Slide |
|---|---|
| 11 | O aparelho: Edge 30 `dubai` |
| 12 | Ambiente: a VM que fabrica, o PC que grava |
| 13 | Fluxo: da VM às partições |
| 14 | Os seis passos da instalação |
| 15 | **Auditoria: 34 subsistemas medidos** |
| 16 | **Problemas de quem opera — e o que generaliza** |
| 17 | O que ficou de pé |
| 18 | Encerramento |

## Slides removidos

- ~~"Medir mudou o que achávamos saber"~~ — removido a pedido
- ~~"Não peço fé. Mostro a régua"~~ (escala CONFIRMADO/RELATADO/RECONSTRUÍDO/AUSENTE) — removido a pedido
- ~~"Quatro provas de que o port funciona"~~ — redundante com o slide 15
- ~~"Da pesquisa à documentação"~~ (cronologia) — cortado por tempo

## Slide 16 — reescrito

Passou a tratar dois pontos que faltavam:

**"Baixa responsividade".** A wiki registra relatos de lentidão no kernel `sc7280-mainline`. Fomos
medir: o toque responde (6942 eventos), a CPU fica 97% ociosa, a GPU acelera até 608 MHz. O que
realmente atrapalha o uso diário é outra coisa — a suspensão trava o aparelho.

**"Cada caso é um caso".** postmarketOS lista 300+ aparelhos, a maioria em `testing`. Dizer que
"suporta o seu modelo" não significa que tudo funciona: depende de quem escreveu o driver daquele
periférico. Nossa matriz vale para **este** Edge 30 — em outro aparelho da mesma distro o resultado
pode ser bem diferente.

É o fecho que liga os dois blocos: **a unidade real de maturidade é o aparelho, não a distribuição.**
