# Falas por integrante — apresentação de 20 minutos

**Tema 10 — Linux em smartphones: distribuições móveis não-Android**
12 slides · turma matutina · 25/11/2026

| Bloco | Integrante | Slides | Tempo |
|---|---|---|---|
| Abertura e o problema | **Luis Eduardo** | 1–2 | ~4 min |
| Arquitetura e as três distros | **Murilo** | 3–4 | ~4 min |
| Comparação e análise crítica | **Ricardo Henrique** | 5–6 | ~4 min |
| Estudo de caso e auditoria | **Pedro Henrique** | 7–9 | ~5 min |
| Limites, resultado e fecho | **Brunno Otavyo** | 10–12 | ~3 min |

> **Regra de ouro:** o slide é apoio, não teleprompter. As perguntas que aparecem na tela são
> ganchos — **a resposta sai da sua boca**, não está escrita lá.

---

## 🎤 LUIS EDUARDO — Abertura e o problema (slides 1–2, ~4 min)

### Slide 1 — Capa (~1 min)

> "Bom dia. Nós somos o grupo do **Tema 10**: Linux em smartphones, distribuições móveis
> não-Android.
>
> Eu sou o Luis Eduardo, e comigo estão Murilo, Pedro Henrique, Ricardo e Brunno.
>
> O trabalho tem duas partes. A primeira é a comparação pedida no tema: **postmarketOS, Mobian e
> Ubuntu Touch**. A segunda é o que a gente acha que dá peso ao trabalho — não ficamos só na
> teoria: **instalamos Linux num celular de verdade** e auditamos o aparelho subsistema por
> subsistema. Trinta e quatro deles."

*Transição:* "Mas antes de comparar, vale entender por que esse problema existe."

### Slide 2 — O problema + Android × Linux (~3 min)

> "Olha o que você tem na mão: um processador ARM de oito núcleos, GPU, oito gigas de RAM,
> armazenamento rápido. Isso é um computador.
>
> Só que o fabricante para de atualizar em dois, três, quatro anos. E aí o aparelho vira lixo
> eletrônico — **com o hardware perfeito**. O que venceu foi o software.
>
> Agora, alguém pode dizer: 'mas Android já é Linux'. É, no kernel. O problema é tudo acima dele.
>
> *(aponta o lado esquerdo)* O Android troca a biblioteca C padrão pela **Bionic**, roda apps numa
> máquina virtual própria, põe uma camada **HAL** entre o sistema e o driver, e usa SurfaceFlinger
> em vez de Wayland. Nada disso é compatível com um programa de Linux comum.
>
> E tem o ponto central: o kernel do Android é **downstream** — milhares de patches do fabricante.
> Quando ele desiste, ninguém mais consegue atualizar.
>
> *(aponta o lado direito)* Do outro lado está o Linux convencional: glibc ou musl, processos POSIX,
> Wayland, systemd, gerenciador de pacotes de verdade. E kernel **mainline** — que recebe correção
> enquanto o código estiver na árvore oficial do Linux."

**A pergunta do slide — responda assim, sem ler:**

> "Daí a pergunta que organiza o trabalho: **dá para rodar esse segundo sistema num celular?**
>
> A resposta curta é **dá, mas não de graça**. E os três projetos que a gente estudou responderam
> de formas bem diferentes: dois decidiram escrever o suporte do zero usando kernel mainline, e um
> decidiu reaproveitar o que o Android já tem. Essa escolha muda tudo — e é ela que a gente vai
> destrinchar agora."

*Passa para o Murilo.*

---

## 🎤 MURILO — Arquitetura e as três distribuições (slides 3–4, ~4 min)

### Slide 3 — A stack em camadas (~2 min)

> "Para comparar os três, primeiro precisamos saber **do que** um Linux móvel é feito. São cinco
> camadas.
>
> Embaixo, o **kernel**. No nosso caso, 7.2.9 mainline, da família sc7280. E aqui tem um detalhe que
> em x86 a gente nem pensa: no PC existe a ACPI, o firmware conta pro sistema o que tem na placa.
> **Em ARM isso não existe.** O hardware é descrito num arquivo chamado **Device Tree** — então
> portar um celular é, em boa parte, escrever esse arquivo.
>
> Acima, o **userspace**: Alpine Linux, gerenciador `apk`, systemd. Mil trezentos e vinte e seis
> pacotes no nosso aparelho.
>
> Depois o **Wayland**, que substituiu o X11. O X11 é dos anos 80 e não lida bem com rotação de
> tela e toque. No Wayland, servidor e compositor são a mesma coisa — o Phoc fala direto com o
> driver de vídeo e manda o trabalho pra GPU via Mesa.
>
> No topo, o **shell móvel**: o Phosh. Um GNOME normal é inutilizável em seis polegadas e meia.
>
> E do lado, a **telefonia** — que é curiosa: o modem é um computador separado, com firmware
> próprio, que conversa por um protocolo chamado QMI. O ModemManager traduz isso pro resto do
> sistema."

### Slide 4 — As três distribuições (~2 min)

> "Com isso na cabeça, as três.
>
> **postmarketOS**, sobre Alpine. A aposta dele é kernel mainline e alcance: mais de trezentos
> aparelhos. Mas atenção — **a maioria está em estágio `testing`**. Ganha em vida longa, perde em
> previsibilidade. Em setembro de 2026 foi rebatizado para **Nura**.
>
> **Mobian** não é uma distro nova: é o **Debian** com pacotes para hardware móvel. Mesma `apt`,
> mesma cultura de estabilidade. Ganha em confiabilidade, perde em alcance — foca em aparelhos
> feitos para Linux, tipo PinePhone.
>
> **Ubuntu Touch**, da comunidade UBports, depois que a Canonical abandonou. Interface própria, a
> Lomiri, e a telefonia mais madura das três. Mas usa **Halium** — e o Ricardo vai explicar por que
> isso é o ponto mais importante da comparação inteira.
>
> Uma coisa que vale notar: **as três usam Wayland**. Duas usam ModemManager. A diferença de fundo
> não está na interface — está no kernel."

*Passa para o Ricardo.*

---

## 🎤 RICARDO HENRIQUE — Comparação e análise crítica (slides 5–6, ~4 min)

### Slide 5 — Comparativo lado a lado (~2 min)

> "Aqui estão as três em oito critérios. Não vou ler a tabela — vou puxar as linhas que importam.
>
> **Base:** Alpine, Debian e Ubuntu. O Alpine usa musl em vez de glibc, o que deixa o sistema bem
> mais leve, mas às vezes quebra compatibilidade com programa fechado.
>
> **Interface:** Phosh nos dois primeiros, Lomiri no Ubuntu Touch. E isso explica uma coisa — como
> postmarketOS e Mobian compartilham o Phosh, o trabalho de um ajuda o outro.
>
> **Telefonia:** ModemManager contra oFono. São dois jeitos de falar com o modem; o ModemManager é
> o mais usado no Linux de desktop hoje.
>
> **Dispositivos:** trezentos e poucos, poucos, e cento e onze. Mas esse número engana, e a gente
> volta nisso no fim.
>
> **E a linha do kernel** — essa é a que decide tudo."

### Slide 6 — mainline × Halium (~2 min)

> "Essa é a conclusão mais importante da nossa comparação: **a diferença que separa os três não é a
> interface, é o kernel.**
>
> De um lado, postmarketOS e Mobian escolheram o caminho **mainline**. Escrevem o Device Tree,
> usam driver da árvore oficial. É muito mais trabalho por aparelho, e a maturidade varia — mas o
> celular continua recebendo kernel novo enquanto aquele código existir no Linux.
>
> Do outro lado, o Ubuntu Touch usa **Halium**: uma camada que reaproveita o kernel e os drivers
> Android do próprio fabricante. Isso faz um aparelho ficar pronto muito mais rápido, e é por isso
> que o Ubuntu Touch tem boa experiência de uso.
>
> **Só que ele herda o kernel congelado do fabricante.** Ou seja: perpetua exatamente o problema que
> motivou o projeto. Você troca o Android por outro sistema, mas continua preso ao kernel que a
> fabricante deixou pra trás.
>
> Então, respondendo de forma prática: **quer usar hoje**, Ubuntu Touch, se seu aparelho estiver no
> catálogo. **Quer estabilidade**, Mobian, em hardware feito pra Linux. **Quer vida longa**,
> postmarketOS.
>
> E tem uma ressalva honesta que a gente faz questão de dizer: **nenhuma das outras duas roda no
> nosso aparelho.** Então o que a gente comparou foram projetos — não três sistemas no mesmo
> hardware. Isso é limite do nosso trabalho."

*Passa para o Pedro.*

---

## 🎤 PEDRO HENRIQUE — Estudo de caso e auditoria (slides 7–9, ~5 min)

### Slide 7 — O aparelho (~1 min)

> "Comparar no papel é fácil. A gente quis ver o que acontece de verdade.
>
> Pegamos um **Motorola Edge 30** — codinome `dubai`. E repare: **não é um aparelho feito para
> Linux**. É um celular de mercado, Snapdragon 778G+, oito núcleos, GPU Adreno.
>
> E a escolha do postmarketOS não foi preferência: **era a única das três com port para esse
> aparelho.** Na prática, foi a realidade que escolheu por nós."

### Slide 8 — Como instalamos (~1,5 min)

> "O processo tem dois ambientes. Uma **VM Ubuntu** que fabrica o sistema, e o **PC** que grava no
> celular.
>
> Na VM roda o `pmbootstrap`, a ferramenta oficial. Ele faz *cross-compile* — compila para ARM numa
> máquina x86 — e cospe três imagens: boot, dtbo e o sistema de arquivos.
>
> No PC, destravamos o bootloader com a chave que a Motorola fornece, desabilitamos a verificação de
> assinatura e gravamos por fastboot.
>
> E aqui uma ressalva: **o método oficial hoje é outro** — usa U-Boot e modo de armazenamento USB. O
> nosso caminho funcionou, mas diverge da documentação, e a gente registrou isso."

### Slide 9 — A auditoria (~2,5 min)

> "Agora a parte que a gente mais gostou de fazer.
>
> Não bastava dizer 'funcionou'. A gente conectou no aparelho por SSH e **mediu trinta e quatro
> subsistemas**, um por um, cada um com saída de comando guardada como evidência.
>
> **Quatorze funcionam.** CPU, display, toque, Wi-Fi 6, Bluetooth, áudio, microfone, bateria. E a
> GPU — essa foi legal de provar: sem conseguir abrir a interface gráfica remotamente, a gente
> mostrou que ela está acelerando porque o compositor mantém o *render node* aberto **e** porque a
> frequência da GPU subiu até 608 MHz, com quase quatrocentas trocas de frequência. Placa parada
> fica na frequência mínima.
>
> **Seis estão detectados mas não validados** — e essa distinção importa muito: aparecer em `/sys`
> **não** quer dizer que funciona. A gente se recusou a pintar de verde o que não mediu.
>
> **Cinco não têm driver:** câmera frontal, NFC, vibração e leitor biométrico.
>
> O número final é **55% de compatibilidade** — e ele vem com a conta aberta: pesos, numerador e
> denominador estão no relatório. Teste que a gente não fez **nunca** entrou como aprovado."

*Passa para o Brunno.*

---

## 🎤 BRUNNO OTAVYO — Limites, resultado e fecho (slides 10–12, ~3 min)

### Slide 10 — Problemas e o que generaliza (~1,5 min)

> "Dois pontos que valem mais que a nossa matriz.
>
> O primeiro: a documentação oficial registra relatos de **'baixa responsividade'** nesse kernel. A
> gente foi medir em vez de repetir. O toque responde — capturamos quase sete mil eventos. A CPU
> fica 97% ociosa. A GPU acelera. **Não é lentidão.**
>
> O que realmente atrapalha o uso diário é outra coisa, e a gente descobriu testando: **a suspensão
> trava o aparelho.** Num modo ela aborta, no outro ela congela e força reinício. Isso não está na
> documentação oficial — é um defeito novo, que a gente pode reportar pro projeto.
>
> O segundo ponto, e esse é o que generaliza: **cada caso é um caso.** O postmarketOS lista mais de
> trezentos aparelhos. Dizer que 'suporta o seu modelo' **não** significa que tudo funciona —
> depende de quem escreveu o driver daquele periférico específico.
>
> Ou seja: nossa matriz vale para **este** Edge 30. Em outro aparelho, mesma distro, o resultado
> pode ser completamente diferente. **A unidade real de maturidade é o aparelho, não a
> distribuição** — e isso é um limite da comparação que a gente apresentou."

### Slide 11 — O que ficou de pé (~1 min)

> "No fim: o aparelho liga em Linux, sobe interface gráfica acelerada, responde ao toque, conecta em
> Wi-Fi 6, toca som, grava do microfone e gerencia bateria. **Zero serviços com falha.**
>
> Classificamos no **nível 3 de 5: estação Linux portátil**. Como computador, ele entrega. Como
> substituto de celular, ainda não — porque a suspensão trava e porque faltam drivers."

### Slide 12 — Encerramento (~0,5 min)

> "Linux no bolso dá. O preço é rigor.
>
> E a gente leva um aprendizado que não esperava: **erramos duas vezes na auditoria.** Concluímos
> que não existia firewall só porque não conseguimos ler as regras — existia, e era bem feito. E
> classificamos o touchscreen como quebrado por medir numa janela de tempo errada — ele sempre
> funcionou.
>
> Os dois erros foram de **raciocínio sobre a evidência**, não de execução de comando. E o segundo
> só foi descoberto porque um de nós **discordou do resultado**, baseado em usar o aparelho todo
> dia.
>
> Fica a lição: a ferramenta acelera, mas não substitui quem conhece o objeto. Obrigado."

---

## Perguntas prováveis da banca

| Pergunta | Quem responde | Resposta curta |
|---|---|---|
| "Por que não testaram no mesmo aparelho as três?" | Ricardo | Só o postmarketOS tem port do Edge 30. Mobian foca em PinePhone/PineTab e o Ubuntu Touch depende de base Halium que não existe para esse modelo. |
| "Dá para usar como celular no dia a dia?" | Brunno | Não ainda. A suspensão trava e faltam câmera frontal, NFC, vibração e biometria. Como computador portátil, sim. |
| "Esse 55% é como?" | Pedro | 16,5 dividido por 30. Funcional vale 1, parcial 0,5. Os 4 não testados saem do denominador, para não reprovar o que não medimos. |
| "Qual a vantagem real sobre o Android?" | Luis Eduardo | Kernel mainline: o aparelho continua recebendo correção depois que o fabricante desiste. E controle total do que roda. |
| "Usaram IA no trabalho?" | Pedro | Sim, Claude Opus 5, declarado no Anexo C. Operou o aparelho por SSH e redigiu a documentação. Errou duas vezes e a gente registrou os erros no artigo. |
| "O que é Device Tree?" | Murilo | Em ARM não há ACPI, então o hardware é descrito num arquivo compilado que o kernel lê no boot. Portar um aparelho é, em boa parte, escrever esse arquivo. |

---

## Checklist antes de apresentar

- [ ] Abrir `presentation/edge30-postmarketos.pptx` (ou o PDF) e testar no projetor
- [ ] Conferir se o aparelho está carregado — se for mostrar ao vivo
- [ ] Cada um treinar o próprio bloco **em voz alta**, cronometrando
- [ ] Combinar as transições: quem fala o nome de quem vem depois
- [ ] Sobra de tempo? Pedro mostra o `audit/dashboard.html` aberto no navegador
- [ ] Levar o artigo impresso ou no e-mail, caso o professor peça
