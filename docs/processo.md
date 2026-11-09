# Registro observado da implementação

Este registro é cronológico. Os bloqueios de uma etapa anterior podem ter sido
resolvidos nas seguintes; o estado mais recente está no sexto retorno abaixo.

## Origem e histórico disponível

Atividade lida: `0e4b9f66-88a6-4c4c-ab50-9cface7855f0_19b - Lab CICD-Pipeline.pdf`,
em Downloads. O enunciado exige CI em push/main e PR/main, CD condicionado ao
sucesso, uso de IA e registro do processo. O pedido do usuário detalha critérios
adicionais e exclui produzir o PDF ou enviar a entrega acadêmica.

O checkout começou na branch `main`, com HEAD abreviado `94efab5` e sem alterações
reportadas por `git status --short`. O remoto observado é
`https://github.com/GustavoCostaAM/about-me.git`. Não havia workflow, pacote npm,
README ou arquivo AGENTS encontrado na árvore do projeto. As instruções AGENTS
fornecidas na conversa também foram consideradas.

Há **6 prompts do usuário** disponíveis neste histórico: o pedido de implementação,
registrado em [prompts.md](prompts.md), o retorno sobre módulos na CI do PR 1,
o terceiro retorno com erros de Ubuntu/linters e o quarto com falha de contexto
do Playwright, o quinto retorno sobre imagens/HTML tratados como CSS e o sexto
sobre três violações dentro do player YouTube de Oppenheimer.
Os retornos estão registrados nas seções correspondentes abaixo.
As mensagens de andamento do agente descrevem a
inspeção, as escolhas, os resultados e os bloqueios; não são novos prompts do usuário.
Existem resumos de conversas anteriores no contexto, não uma transcrição completa;
não foram usados para inventar interações nem contar prompts históricos.

## Evolução e problemas

| Ação observada | Resultado/problema | Alteração ou consequência |
| --- | --- | --- |
| Inspeção de arquivos, status e remoto | 6 HTML, 4 CSS e imagens, sem configuração de CI | Escolhida pipeline para site estático inteiro |
| Leitura do PDF com pypdf | Primeira impressão no terminal falhou por encoding cp1252 | Reexecutada a extração com saída UTF-8; enunciado lido |
| Procura de instruções no checkout | Nenhum AGENTS local encontrado | Usadas as instruções fornecidas na conversa |
| Uso de `rg` e `gh` | Executáveis não encontrados | Inspeção por PowerShell/Git; nenhuma ação remota via gh |
| `git ls-remote origin HEAD` | Falha `getaddrinfo() thread failed to start` | Estado remoto não confirmado |
| Consulta npm e geração de lock | `ENOTFOUND registry.npmjs.org` | Dependências não instaladas e lock não gerado |
| Criação de `feat/ci-cd-pages` | Git não conseguiu criar `.git/refs/heads/feat/ci-cd-pages` | Checkout permanece em main; nenhum commit criado |
| Tentativa de checkout isolado em C:/workspace | Permissão negada ao criar diretório | Não há branch alternativa nem metadados Git modificados |
| Tentativas de consulta ao Pages | Sem acesso pela consulta web; navegador reportou tab fora da sessão | Origem e URL reais continuam pendentes de inspeção |
| Primeiro teste de integridade | 4 erros locais: IDs duplicados em dois documentos, favicon ausente e âncora Projetos ausente | Referências corrigidas, conforme tabela abaixo |
| Nova montagem e integridade | 40 arquivos públicos; 6 páginas sem erros locais | Manifestos e JSON gerados em reports |
| Testes do verificador | 8 testes passaram | Cobertura de caixa, acentos, URLs, âncoras e inventário |
| Checker de URLs externas | Falhas DNS viraram warnings; comando terminou com código 0 | Diagnósticos preservados; não são prova de indisponibilidade dos sites |
| Checagem sintática de accessibility.mjs | `node --check` terminou com código 0 | Não comprova execução do navegador ou axe |
| Tentativas dos comandos de lint e acessibilidade | html-validate e stylelint não encontrados; teste axe terminou com ERR_MODULE_NOT_FOUND para playwright | Confirmado bloqueio por dependências ausentes, sem auditoria executada |
| Parse dos dois YAML com PyYAML | Dois arquivos lidos, triggers e jobs identificados | Não substitui avaliação de expressões pelo Actions |
| Parse CSS suplementar com tinycss2 já disponível | Nenhum erro de parse nas quatro folhas | Não substitui o Stylelint |
| Parse HTML suplementar com lxml já disponível | Parser HTML4 reportou tags HTML5 como desconhecidas | Resultado inadequado para validar HTML5; não contado como aprovação |
| `git diff --check` | Sem diagnóstico, código 0 | Não é execução dos linters |

## Alterações feitas pelo agente

- Criados `.github/workflows/ci.yml` e `.github/workflows/cd.yml`, com validação
  separada da publicação e gates por evento, resultado, repositório e SHA.
- Criados `package.json`, configurações de lint, configuração de URL/viewport,
  montagem, integridade, teste HTTP com Playwright/axe e testes do verificador.
- Criados README e registros de operação, processo e prompt.
- Substituídos os dois `id="link"` duplicados por classes em cada página afetada.
- Corrigidos o favicon da entrada do GerminaFlix e a âncora de Projetos.
- URLs locais com espaços/acentos passaram a usar percent encoding. Nenhum arquivo
  de imagem ou diretório público foi renomeado.
- Botões dentro de links passaram a ser links estilizados, com foco visível.
- Adicionados textos alternativos/alternativas vazias apropriadas e idioma pt-BR
  nas páginas em português; corrigida a alternativa que descrevia outro filme.
- Títulos foram retirados do interior de listas, com um título principal por página
  e hierarquia no catálogo. Conteúdo da página pessoal e detalhes está sob main.
- A entrada GerminaFlix deixou de redirecionar em dois segundos: apresenta logo,
  título e link explícito para abrir o catálogo. Isso permite ler, navegar e testar
  a própria página sem ela desaparecer. A animação que ocultava a entrada saiu.
- Ajustados CSS de navegação, apresentação, catálogo e detalhes: cores de controles
  e rodapé, foco visível, espaçamento/alvos e barras de rolagem do catálogo; nomes
  de seletores normalizados. Essas mudanças visuais ainda aguardam lint e axe reais.
- Na página de Oppenheimer, pôster e link IMDb copiados de Havog foram corrigidos
  para o filme da própria página. O trailer existente foi mantido.
- Removido atributo obsoleto frameborder; borda controlada por CSS. Dimensões HTML
  numéricas corrigidas e entidades de copyright/ampersand ajustadas.

Não foi observado trabalho manual do usuário durante esta implementação. Não foi
usado agente adicional. Nenhuma configuração remota foi alterada, nenhum merge,
deployment, PDF ou envio acadêmico foi realizado.

## Validação concluída versus pendências

**Validado localmente:** montagem do conjunto público, inventário das seis páginas,
referências locais, oito testes de integridade, execução não bloqueante do checker
externo sob falha DNS, sintaxe JavaScript, parse YAML e parse CSS suplementar.

**Implementado mas não validado:** lint HTML/CSS das ferramentas escolhidas,
servidor/navegador/axe, workflows no Actions, guards/API do CD e integração Pages.

**Bloqueado antes de abrir PR:** gerar/versionar lock, instalar dependências e
Chromium, executar a suíte completa, corrigir qualquer resultado, criar branch e
commits, push, PR e acompanhar CI. Não existe link de PR ou execução do Actions
para anexar. O código continua no checkout original, com alterações não commitadas.

**Aguardará revisão e merge:** coordenação da origem Pages para Actions imediatamente
antes do merge, sucesso da CI de push/main e primeiro CD real. Esses resultados
futuros devem ser adicionados aqui com links verdadeiros, seguindo o procedimento
de [ci-cd.md](ci-cd.md).

Links disponíveis agora: [repositório informado](https://github.com/GustavoCostaAM/about-me)
e [lista genérica de Actions](https://github.com/GustavoCostaAM/about-me/actions).
A lista de Actions não é evidência de uma execução desta implementação.

O [snapshot local](validacao-local.json) preserva o inventário, resultados
observados e hashes dos arquivos públicos. Os JSON completos regeneráveis ficam
em reports, ignorados pelo Git e excluídos da publicação.

## Continuação em ambiente com permissões e rede

### Retorno do usuário: falha de módulos na CI do PR 1

Segundo prompt observado, após a implementação inicial:

> deu erro ao rodar pipeline de ci, veja no github: https://github.com/GustavoCostaAM/about-me/actions/runs/42546199608/job/128931638785?pr=1
>
> os erros são relacionados ao tentar encontrar modulos

O checkout agora está na branch `feature/ci-cd`, com commit `36697d1`, e o usuário
forneceu um link de execução do PR 1. Isso atualiza o estado anterior: há trabalho
commitado e uma execução remota informada. Não foi possível ler seus logs pelo
acesso web nem pela integração de diagnósticos; a causa remota exata não foi
confirmada. O link é evidência fornecida pelo usuário, não uma execução inspecionada.

No checkout, `package-lock.json` continua ausente e não está versionado. Isso impede
`npm ci` e o cache npm de setup-node. As condições `!cancelled()` permitiam executar
linters e axe mesmo depois da falha de instalação, causando falhas secundárias por
dependências ausentes. A nova tentativa de gerar o lock falhou com
`ENOTFOUND registry.npmjs.org`.

O agente adicionou diagnóstico explícito para lock ausente, instalação com
`npm ci --include=dev`, uso do Playwright local com `npx --no-install` e condições
de sucesso dos pré-requisitos antes das verificações. A instalação continua
obrigatória e qualquer falha continua bloqueando CI e CD. Não foi trocada por uma
resolução não determinística de dependências durante o Actions.

**Pendência bloqueante:** gerar e versionar o lock em ambiente com acesso npm,
executar a suíte e acompanhar nova CI. Estas alterações locais não comprovam a
correção da execução remota informada.

### Terceiro retorno: Ubuntu, opção de CLI e especificidade CSS

Prompt do usuário:

> os seguintes erros foram encontrados:

```text
Run npx --no-install playwright install --with-deps chromium
BEWARE: your OS is not officially supported by Playwright; installing dependencies for ubuntu26.04-x64 as a fallback.
Cannot install dependencies for ubuntu26.04-x64 with Playwright 1.55.1!
Failed to install browsers
Error: ERROR: Playwright does not support chromium on ubuntu26.04-x64

 about-me@1.0.0 lint:html
> html-validate "**/*.html" --ignore-pattern node_modules/** --ignore-pattern dist/** --ignore-pattern reports/**

unknown option --ignore-pattern

> about-me@1.0.0 lint:css
> stylelint "**/*.css" --ignore-pattern node_modules/** --ignore-pattern dist/**

style.css
  154:1  ✖  Expected selector "footer a" to come before selector "a:focus-visible", at line 23  no-descending-specificity

✖ 1 problem (1 error, 0 warnings)
```

Na inspeção deste retorno, o HEAD é `c7ba02b`, branch `feature/ci-cd`, e o lock já
está versionado. As cinco dependências de desenvolvimento estão disponíveis.
Isso supera os bloqueios anteriores de ausência de lock e pacotes neste checkout.

Correções do agente:

- Fixado runner `ubuntu-24.04`, compatível com a versão fixada do Playwright,
  evitando a mudança implícita do sistema por `ubuntu-latest`.
- Substituída a opção inexistente `--ignore-pattern` do HTML Validate pelo arquivo
  `.htmlvalidateignore`, com somente node_modules, dist e reports.
- Reordenados `footer a`, `a:focus-visible` e `a[aria-current="page"]` para manter
  a regra de especificidade ativa. Uma primeira reordenação revelou conflito também
  com `.ul-header a`; a ordem final resolveu os dois diagnósticos, sem mudar valores.
- A execução efetiva de HTML Validate revelou mais 11 erros: SRI ausente nos links
  de estilos e duas regiões de catálogo com elemento não nativo. Adicionados hashes
  SHA-384 e trocados os wrappers por section, mantendo classes, nomes e tabindex.
- Adicionados comando `update:sri`, verificação de SRI desatualizado e dois testes
  de regressão. `.gitattributes` fixa LF para evitar divergência dos hashes entre
  Windows e Linux. Nenhuma regra ou página-fonte foi suprimida.
- A execução via launchers `.cmd` locais falhou buscando html-validate fora do
  projeto. Os scripts npm agora chamam os entrypoints dos CLIs instalados pelo Node.

Validações observadas:

| Comando | Resultado |
| --- | --- |
| `npm run lint` | HTML e CSS aprovados, código 0 |
| `npm run test:integrity` | 10 testes aprovados |
| `python tools/site.py check` | 6 páginas e 40 arquivos públicos, sem erros locais/SRI |
| `python tools/site.py build` | Bloqueado por WinError 5 ao remover dist/germinaFlix/main no Windows |
| `node tools/accessibility.mjs` | Reprovou antes da auditoria: Chromium não instalado no cache deste ambiente |

A nova CI Linux ainda não foi observada neste retorno. A compatibilidade do runner
e os resultados de axe devem ser confirmados nela. As alterações acima estão no
checkout, sem commit/push realizados pelo agente. Não houve merge ou deployment.

### Quarto retorno: contexto explícito para axe/Playwright

Trecho literal do prompt recebido (o log completo repete o mesmo erro nas seis
páginas listadas pelo teste):

> agora erro em acessibilidade:

```text
Error: Please use browser.newContext()
```

O log fornecido pelo usuário lista as seis páginas e uma falha de execução em
`AxeBuilder.analyze()` para cada uma. Não representa seis violações WCAG: o axe
não conseguiu concluir as auditorias.

O script criava a página com `browser.newPage()`. O agente verificou o código
instalado do axe e sua documentação de tratamento de erros: a análise usa páginas
temporárias para combinar resultados de frames. Alterado para
`browser.newContext({ viewport })` seguido de `context.newPage()`, por HTML. O
finally agora fecha o contexto inteiro, incluindo suas páginas temporárias.

Viewport, descoberta das seis páginas, tags WCAG, target-size e critérios de
erro/aviso foram mantidos. Não foi ativado modo legado nem excluído iframe,
regra ou página. `node --check tools/accessibility.mjs` passou, assim como a
checagem de whitespace do diff. A tentativa de `npm run test:a11y` reprovou antes
de abrir qualquer página: o executável Chromium não existe no cache do ambiente
local. Não houve confirmação da correção em execução remota neste retorno.

### Quinto retorno: arquivos de dist recebidos como CSS

Trechos literais do prompt do usuário, com resumo explícito do restante do log:

> agora tem erro de lint em css

```text
> node node_modules/stylelint/bin/stylelint.mjs "**/*.css" --ignore-pattern node_modules/** --ignore-pattern dist/**

dist/images/homePage/LinkedIn.png
  9:135  ✖  Unclosed string  CssSyntaxError

dist/index.html
  1:1  ✖  Unknown word <  CssSyntaxError

✖ 32 problems (32 errors, 0 warnings)
```

O restante do log contém diagnósticos semelhantes em outras imagens e no HTML de
Projetos em dist. São entradas de tipo errado, não violações nas folhas CSS.
Os globs `node_modules/**` e `dist/**` dos argumentos de ignore estavam sem aspas:
no shell Linux podem expandir em vários caminhos antes de chegar ao Stylelint.
Os caminhos extras viram entradas posicionais e acabam analisados como CSS.

O agente moveu as exclusões para `.stylelintignore`, com node_modules, dist e
reports, removendo esses argumentos da linha de comando. O único glob restante
é `"**/*.css"`, entre aspas, para seleção pelo próprio Stylelint. Adicionado
`--formatter verbose` para registrar os arquivos efetivamente analisados.
Nenhuma folha-fonte ou regra de lint foi excluída, e nenhum binário foi alterado.

Validação observada: `npm run lint:css` terminou com código 0, **4 sources checked**
e **0 problems found**. A lista contém style.css, germinaFlix/main/style.css,
germinaFlix/saiba Mais/style.css e projects/css/style.css. A pasta dist existia
com 34 HTML/imagens no momento da validação; nenhum deles apareceu na lista do
Stylelint. `git diff --check` também passou. A nova CI Linux ainda não foi
acompanhada neste retorno; alterações permanecem locais, sem commit/push do agente.

### Sexto retorno: semântica do player YouTube incorporado

Trecho literal do prompt:

> erro de semantica para tags html:

```text
germinaFlix/saiba Mais/oppenheimer/index.html: 3 errors; 0 incomplete rules
```

Resumo explícito do restante do log fornecido pelo usuário: as outras cinco páginas
apresentaram zero erros e zero regras incompletas. Em Oppenheimer, as três regras
foram `aria-allowed-attr`, `aria-prohibited-attr` e `button-name`. Seus targets
começam por iframe e apontam para `.ytmVideoInfoVideoTitle`, `#movie_player` e
`.ytmVideoInfoChannelAvatar`, respectivamente. Portanto, os elementos problemáticos
estão no conteúdo do player incorporado, não nas tags do documento hospedeiro.

O agente substituiu somente o iframe de Oppenheimer por uma seção com título
associado e link nativo descritivo para o mesmo vídeo, ID `F3OxA9Cz17A`. A página
agora informa que o trailer abre no YouTube, em vez de oferecer reprodução
incorporada. O trailer continua acessível. A integração de Havog, sem violações no
log fornecido, foi mantida.

Nenhum seletor, iframe remanescente, regra ou página foi excluído do axe. As três
violações não foram reclassificadas como warnings. A mudança corrige a composição
do conteúdo oferecido pela página, sem tentar alterar a DOM de terceiros.

Após a alteração, `npm run lint` aprovou HTML e as quatro folhas CSS (zero
problemas); `npm run check:links` aprovou as seis páginas e os 40 arquivos públicos.
`git diff --check` passou. Não houve nova execução de axe neste retorno, pois o
Chromium local segue indisponível conforme registrado anteriormente. Nenhuma
aprovação remota de acessibilidade foi observada após a mudança. Alterações ainda
locais, sem commit/push do agente e sem deployment.

### Pendências originais (registro histórico)

Manter as alterações locais. Criar `feat/ci-cd-pages`, gerar o lock, executar todos
os comandos de validação e corrigir as ferramentas escolhidas sem relaxar regras.
Inspecionar Pages e ajustar o prefixo se a hipótese `/about-me/` não corresponder
à configuração real. Atualizar os registros com os resultados efetivos, criar os
commits, fazer push e abrir PR para main. Acompanhar até a aprovação da CI do PR.
Não fazer merge nem antecipar deployment. A presente limitação é ambiental, não
uma solicitação de aprovação para trabalho que já foi autorizado.
