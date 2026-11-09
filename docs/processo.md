# Registro observado da implementação

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

Há **1 prompt de implementação** diretamente disponível nesta execução, registrado
em [prompts.md](prompts.md). As mensagens de andamento do agente descrevem a
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

Manter as alterações locais. Criar `feat/ci-cd-pages`, gerar o lock, executar todos
os comandos de validação e corrigir as ferramentas escolhidas sem relaxar regras.
Inspecionar Pages e ajustar o prefixo se a hipótese `/about-me/` não corresponder
à configuração real. Atualizar os registros com os resultados efetivos, criar os
commits, fazer push e abrir PR para main. Acompanhar até a aprovação da CI do PR.
Não fazer merge nem antecipar deployment. A presente limitação é ambiental, não
uma solicitação de aprovação para trabalho que já foi autorizado.
