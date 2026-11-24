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
