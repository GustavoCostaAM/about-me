# CI/CD do apresentacaoPessoal

## Estado da implementação

Os arquivos foram escritos no checkout local, mas a implementação **ainda não
atingiu os critérios de aceite**. Não fazer merge neste estado.

O lock está versionado e as dependências estão presentes no checkout. Lint HTML,
lint CSS, integridade das seis páginas e dez testes do verificador passaram após
as últimas correções. O checkout está em `feature/ci-cd`, com base em `c7ba02b`;
as correções deste retorno ainda são locais. Falta acompanhar nova CI do PR 1,
validar Chromium/axe e confirmar Pages. A auditoria local não iniciou por falta
do navegador; a remontagem de dist também encontrou permissão negada no Windows.

## Fluxo preparado

1. `CI` executa em pushes na `main` e PRs destinados à `main`.
2. No runner fixo Ubuntu 24.04 (compatível com Playwright 1.55.1), faz checkout sem
   persistir credenciais, configura Node 22.18.0 e Python 3.11,
   instala pelo lock com `npm ci` e instala Chromium do Playwright.
3. Monta `dist/`, executa os dois linters, testes do verificador, integridade local,
   disponibilidade externa e acessibilidade HTTP de todas as páginas.
4. Preserva os relatórios mesmo em falhas. Somente um push aprovado na `main`
   produz o artefato `github-pages`.
5. O workflow separado `CD - GitHub Pages` recebe `workflow_run` concluído de `CI`.
   O job exige sucesso, evento original `push`, branch `main` e repositório original
   igual ao atual. PR, cancelamento, falha ou outra branch não habilitam o job.
6. O CD compara `head_sha` com a ponta atual de `main`, baixa o artefato pelo ID
   exato da execução de CI e transfere o mesmo `artifact.tar` para sua execução.
   Não faz checkout, instalação ou reconstrução no job com permissão de publicar.
7. Confere URL e origem do Pages, revalida `main` e chama `deploy-pages`.

A concorrência global `github-pages-production`, sem cancelar a execução ativa,
serializa publicações. Mesmo se uma CI antiga terminar depois de outra recente,
seu SHA não corresponderá à ponta de `main` e a publicação será ignorada. A segunda
checagem reduz a janela de mudança de `main` durante a preparação. Se houver um
push após essa checagem, a publicação em curso termina antes de qualquer próxima
publicação; uma versão antiga não pode executar depois de uma nova já publicada
pelo mesmo grupo. Cancelamentos de CI não produzem releases.

O `workflow_run` precisa existir na branch padrão para disparar. Assim, a abertura
do PR permite validar CI, mas não valida a integração de CD. Não há `workflow_dispatch`.

## Ferramentas e justificativa

| Ferramenta | Finalidade |
| --- | --- |
| HTML Validate, presets recommended/document/a11y | Estrutura, sintaxe, atributos, referências entre IDs e semântica HTML |
| Stylelint e config-standard | Sintaxe CSS, propriedades, valores e convenções, sem desabilitar regras |
| Python, biblioteca padrão | Descoberta de arquivos, montagem pública, resolução de links sem depender do comportamento de caixa do Windows |
| Playwright + Chromium | Carregamento real do site por HTTP com viewport desktop fixa |
| axe-core via @axe-core/playwright | Regras automáticas aplicáveis de WCAG e boas práticas, diagnóstico por regra e nó |
| GitHub Pages e actions oficiais | Hospedagem estática existente, artefato Pages e autorização OIDC sem PAT de deployment |

As versões diretas estão fixadas no `package.json` e as transitivas no lock
versionado. O workflow usa `npm ci --include=dev` e reprova ausência ou divergência
do lock, em vez de resolver versões silenciosamente na CI.

## Instalação e comandos locais

Pré-requisitos: Node 22.18.0, npm 10, Python 3.11, acesso ao registro npm e ao download
do Chromium. Com o lock versionado, instalar e validar:

```sh
npm ci --include=dev
npx playwright install --with-deps chromium
npm run test:integrity
npm test
```

Se mudar versões de dependências, atualizar/revisar o lock e versioná-lo na mesma
branch. Nas instalações usar `npm ci`, que rejeita divergências com o manifesto.

| Comando | Verificação/resultado |
| --- | --- |
| `npm run build` | Monta `dist/` e `reports/public-files.json` |
| `npm run lint:html` | Lint de todos os HTML do site |
| `npm run lint:css` | Lint de todos os CSS do site |
| `npm run check:links` | Integridade local sem rede; `reports/integrity.json` |
| `npm run update:sri` | Atualiza SHA-384 dos estilos/scripts locais e normaliza CSS para LF |
| `npm run check:external` | HEAD, fallback GET e diagnóstico externo em `reports/external-links.json` |
| `npm run test:a11y` | Servidor HTTP temporário, Chromium e axe; `reports/accessibility.json` |
| `npm run test:integrity` | Testes de regressão do verificador |
| `npm test` | Montagem, lint, integridade, links externos e acessibilidade |

O servidor é criado dentro do teste de acessibilidade, usa porta livre em loopback,
aceita somente arquivos do manifesto e fecha ao terminar. Não é necessário iniciá-lo
manualmente. Rodar `build` antes de `test:a11y` para não testar uma cópia antiga.

HTML Validate usa `.htmlvalidateignore` para ignorar somente dependências e saídas
geradas, sem excluir páginas-fonte do site. Os dois CLIs são chamados pelo Node,
evitando um problema observado nos launchers `.cmd` locais do Windows. O glob
continua cobrindo todos os arquivos HTML/CSS do site.

Stylelint usa `.stylelintignore` para node_modules, dist e reports. Não há globs
de exclusão sem aspas na linha de comando: isso evita que o shell Linux os expanda
em arquivos extras passados como entradas. O modo verbose lista as folhas
efetivamente verificadas, permitindo conferir a cobertura no log da CI.

As folhas locais têm SRI SHA-384 nos HTML. Após editar CSS, executar
`npm run update:sri` e versionar os HTML atualizados junto com o CSS. O checker de
integridade reprova hashes desatualizados, para impedir que o navegador recuse os
estilos publicados. `.gitattributes` fixa LF para CSS/HTML, preservando no Linux
os mesmos bytes usados nos hashes; não há regeneração silenciosa de hashes na CI.

## Site e escopo público

`site.config.json` usa `https://gustavocostaam.github.io/about-me/` como hipótese de
URL padrão, derivada do nome do repositório informado. **A URL real, eventual CNAME
e a origem configurada no Pages ainda precisam ser inspecionados.** Se houver
domínio personalizado, atualizar configuração, guard do CD e testes antes de avançar.

A descoberta percorre recursivamente todos os arquivos estáticos, inclusive páginas
sem links. Não depende de um crawler alcançar as páginas. Exclui pastas de
desenvolvimento (`tools`, `docs`, `reports`, `dist`, `node_modules`, nomes começando
com ponto), manifestos npm e configuração de testes. Copia HTML, CSS, imagens,
scripts, mídia, fontes e outros formatos públicos listados em `tools/site.py`.
Inclui `CNAME` caso exista e adiciona `.nojekyll`. Os nomes dos arquivos e diretórios
existentes, inclusive espaços e acentos, são preservados.

Inventário observado: **6 HTML, 4 CSS e 30 imagens**, total de **40 arquivos públicos**
mais `.nojekyll` gerado. O manifesto público e os relatórios são artefatos da CI;
não são publicados junto com o site.

| Página descoberta | Status observado |
| --- | --- |
| `index.html` | Integridade aprovada; axe pendente |
| `projects/projects.html` | Integridade aprovada; axe pendente |
| `germinaFlix/index.html` | Integridade aprovada; axe pendente |
| `germinaFlix/main/index.html` | Integridade aprovada; axe pendente |
| `germinaFlix/saiba Mais/havog/index.html` | Integridade aprovada; axe pendente |
| `germinaFlix/saiba Mais/oppenheimer/index.html` | Integridade aprovada; axe pendente |

O verificador resolve caminhos relativamente ao documento ou CSS, decodifica percent
encoding, mantém a caixa real dos nomes mesmo no Windows e confere âncoras HTML.
URLs absolutas do mesmo host são locais e precisam permanecer sob `/about-me/`.
Referências que escapam do prefixo, arquivos ausentes e IDs duplicados são erros.
`src`, `href`, `srcset`, `poster`, objetos, formulários, refresh e CSS `url()`/imports
são inspecionados. Sintaxes não suportadas, como `<base>`, data URL em `srcset` e URL
CSS com escapes, geram erro explícito. Não há esses casos no site observado.

## Acessibilidade: cobertura e limites

Viewport: **1440 × 900 pixels**, Chromium desktop, contexto explícito isolado e
nova página para cada HTML (`browser.newContext()` → `context.newPage()`). O contexto
é fechado no finally da página, incluindo as páginas temporárias abertas pelo axe
para combinar resultados de frames. Não é usado o modo legado do axe.
Tags: `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa` e `best-practice`.
A regra `target-size` é explicitamente habilitada para incluir sua verificação
disponível de WCAG 2.2 AA. Nenhuma página, seletor ou regra foi excluída para
contornar falhas. A lista efetiva de passes, regras não aplicáveis, violações e
resultados incompletos será registrada por página, com a versão efetiva do axe.

O teste verifica nomes acessíveis, alternativas textuais, landmarks, títulos,
semântica de listas, relações ARIA, contraste quando determinável, foco/elementos
interativos e as demais regras aplicáveis da versão instalada. Falta de resultados
para uma página também reprova. Uma auditoria só é aprovada quando todas as páginas
descobertas têm resultado e não há violações nem erros de execução locais.

**Aprovação automática não certifica conformidade integral com WCAG 2.2 AA.** Axe
não resolve todos os critérios, a qualidade de toda descrição, a experiência completa
de teclado/leitor de tela, legendas adequadas ou compreensão do conteúdo. Frames de
terceiros podem produzir limitações de inspeção e resultados incompletos. Esses
itens são registrados, sem fingir que foram avaliados por uma pessoa. Não há teste
mobile nem avaliação manual de acessibilidade neste escopo.

## Erros e avisos

| Evento | Tratamento |
| --- | --- |
| Erro de HTML/CSS | Bloqueia CI |
| Arquivo local/âncora ausente, diferença de caixa, escape do prefixo | Bloqueia CI |
| Falha do servidor, navegador, axe, página HTTP local ou script | Bloqueia CI |
| Qualquer `violation` do axe, inclusive impacto minor e boas práticas | Bloqueia CI |
| `incomplete` do axe, dependente de julgamento humano | Aviso registrado, sem bloquear |
| DNS, timeout, HTTP inválido ou outra indisponibilidade de URL externa | Aviso com URL e diagnóstico, sem bloquear |
| Falha interna do próprio verificador | Bloqueia CI, não é tratada como indisponibilidade externa |

O checker externo tenta HEAD e depois GET, com timeout por tentativa e concorrência
limitada. Não valida o conteúdo ou fragmentos de sites de terceiros. Warnings
externos não comprovam que um link está errado; podem refletir bloqueio de robôs
ou rede local. A CI mantém suas mensagens, anotações de warning e JSON.

## GitHub e migração do Pages

Antes de merge, concluir instalação, todas as validações locais e CI do PR.
Confirmar pelo GitHub a origem atual, URL, domínio e regras de ambiente. Não há
evidência disponível dessas configurações neste ambiente.

Se a origem atual for uma branch, mantê-la durante a revisão para preservar o fluxo
atual de atualizações. **Ao encerrar a revisão, imediatamente antes do merge**,
selecionar Settings → Pages → Build and deployment → Source → GitHub Actions.
Não fazer pushes de produção entre essa troca e o merge. O site já publicado
deve permanecer disponível, mas confirmar isso no endereço existente.

Essa coordenação é necessária: se a origem por branch continuar ativa no momento do
merge, o publicador antigo do GitHub pode publicar o commit sem esperar esta CI.
O workflow CD exige `build_type: workflow` e falha com diagnóstico se a migração
não foi feita. Não executa mudanças de configuração durante o PR nem antecipa CD.

Permitir GitHub Actions no repositório e uso das actions oficiais. Configurar
`github-pages` para aceitar `main`; observar eventuais aprovações obrigatórias do
ambiente, que impedem CD inteiramente automático. Recomenda-se proteger `main`
exigindo `CI / validate`, após seu primeiro resultado real. Não há PAT, secrets
personalizados ou credencial de longa duração no fluxo. CI tem `contents: read`;
CD tem apenas `contents: read`, `actions: read`, `pages: write`, `id-token: write`.

## Validação após merge pelo usuário

1. Confirmar que o push do merge iniciou `CI`, com evento `push`, branch `main` e SHA
   do commit do merge. O SHA sintético da CI de PR não serve como evidência de CD.
2. Conferir sucesso de todos os checks e baixar `validation-reports`. Comparar as
   páginas descobertas, resultados axe e manifesto de arquivos públicos.
3. Conferir que `CD - GitHub Pages` foi habilitado por esse mesmo ID de CI e SHA.
   Verificar o diagnóstico dos guards e a origem configurada como Actions.
4. Confirmar sucesso do deployment e registrar URL da CI, CD e commit publicado em
   `docs/processo.md`. Não inventar esses links antes de existirem.
5. Abrir apresentação, Projetos, entrada, catálogo e as duas páginas de detalhes do
   GerminaFlix no endereço público existente. Conferir imagens/CSS e URLs codificadas
   com espaço/acento. Isso é smoke test de publicação, não avaliação manual WCAG.
6. Para validar bloqueio por erro e cancelamento, usar PRs e inspecionar que nenhum
   artefato de release/CD foi produzido. Só executar cenários adicionais de produção
   após o merge se desejado e sob controle do proprietário.

## Referências das ferramentas

- [Eventos workflow_run](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run)
- [Concorrência no Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
- [Workflow personalizado do Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Presets do HTML Validate](https://html-validate.org/rules/presets.html)
- [Regras do axe-core](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md)
- [Configuração padrão do Stylelint](https://github.com/stylelint/stylelint-config-standard)

As referências explicam as ferramentas; não são evidência de que este repositório
executou seus workflows.
