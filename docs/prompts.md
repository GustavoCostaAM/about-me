# Prompt observado nesta execução

Há um prompt de implementação disponível. Transcrição do pedido do usuário abaixo.
As instruções de contexto/AGENTS e os resumos anteriores não foram contados como
prompts de implementação nem reconstruídos como se fossem transcrições.

---

Implemente CI/CD no projeto atual `apresentacaoPessoal`, atendendo à atividade “Lab CICD-Pipeline”, disponível em Downloads.

## Contexto e objetivo

O projeto é um site estático em HTML/CSS, vinculado ao repositório `https://github.com/GustavoCostaAM/about-me`, e já está publicado no GitHub Pages.

Utilize esse projeto como base para demonstrar integração contínua e publicação automática pelo GitHub Actions. Publique o site inteiro, incluindo a apresentação pessoal, Projetos, GerminaFlix e todas as páginas internas, imagens e estilos.

Leia as instruções do repositório e o enunciado da atividade antes de implementar. Inspecione a configuração atual do Pages e preserve o endereço público existente.

## Decisões já aprovadas

- Criar **dois workflows separados**: um para CI e outro para CD.
- Executar CI em cada push na `main` e em pull requests destinados à `main`.
- Executar CD automaticamente após push na `main`, somente quando a CI correspondente tiver sucesso.
- Utilizar GitHub Pages como destino.
- Aplicar lint e testes automáticos de acessibilidade.
- Adotar **WCAG 2.2 nível AA**, com cobertura dos critérios verificáveis pelas ferramentas escolhidas.
- Testar acessibilidade em **desktop**, em todas as páginas HTML.
- Erros devem reprovar a CI e impedir o CD. Avisos não devem bloquear.
- Verificar links externos; indisponibilidade externa deve gerar apenas avisos.
- Permitir adição de `package.json`, arquivo de lock e dependências de desenvolvimento.
- Deixar a escolha das ferramentas a seu critério, justificando-a na documentação.
- Permitir correções no HTML, CSS, conteúdo e apresentação quando necessárias para resolver problemas encontrados.
- Registrar prompts, interações relevantes, alterações, problemas e validações no repositório.
- Criar branch, commits, push e PR, deixando o PR aberto para revisão.
- **Não fazer merge. O CD será testado somente após o merge pelo usuário.**
- Não produzir o PDF da atividade nem enviar a entrega acadêmica.

## CI

Implemente verificações reproduzíveis localmente e no GitHub Actions.

O workflow deve realizar checkout, preparar o ambiente, instalar as dependências de forma determinística e executar as verificações. Disponibilize comandos locais equivalentes.

### Lint e integridade do site

Cubra HTML e CSS de forma abrangente e adequada ao projeto. Inclua verificação de:

- Estrutura e sintaxe dos documentos.
- Referências a páginas, imagens, estilos e outros arquivos locais.
- Caminhos relativos, diferenças entre maiúsculas e minúsculas e nomes com espaços ou acentos.
- Âncoras internas e destinos locais.
- Links externos, com falhas de disponibilidade classificadas como avisos.

As verificações de arquivos locais devem funcionar no ambiente Linux do Actions e considerar o caminho de publicação real do GitHub Pages.

Erros locais devem bloquear a CI. Trate falhas externas de forma que não reprovem o pipeline, sem ocultar seu diagnóstico.

### Acessibilidade

Sirva o site por HTTP e execute testes automáticos em todas as páginas HTML, inclusive páginas internas do GerminaFlix.

Configure as regras aplicáveis a WCAG 2.2 A e AA disponíveis na ferramenta escolhida. Documente a cobertura e suas limitações: aprovação automática não equivale a certificação de conformidade integral.

Use viewport desktop e registre suas dimensões. Não inclua avaliação manual de acessibilidade nem testes mobile no escopo.

A descoberta ou listagem das páginas deve permitir comprovar que todas foram verificadas. Falhas ao iniciar o servidor, carregar uma página ou executar a ferramenta devem reprovar a CI.

Separe erros de avisos de forma explícita. Violações automáticas classificadas como erros devem bloquear; avisos e itens que dependem de avaliação humana devem ser registrados sem bloquear.

### Correções

Execute as verificações e corrija os problemas encontrados até obter aprovação. Não enfraqueça regras, exclua páginas, suprima erros ou transforme violações em avisos apenas para fazer a CI passar.

Há autorização para corrigir o site sem restrições específicas de conteúdo ou aparência. Mantenha as alterações relacionadas aos problemas identificados e registre mudanças visuais ou de conteúdo relevantes.

## CD

Implemente a publicação no segundo workflow, mantendo a dependência entre CI e CD mesmo com arquivos separados.

Garanta que:

- Somente o sucesso da CI de um **push na `main`** possa habilitar a publicação.
- Uma CI de PR ou de outra branch não provoque deployment.
- O conteúdo publicado corresponda ao **mesmo commit aprovado pela CI**, sem usar inadvertidamente outro estado da `main`.
- Falha ou cancelamento da CI impeça o deployment.
- Execuções concorrentes não façam uma versão antiga substituir uma mais recente.
- O artefato publicado contenha o site inteiro, excluindo ferramentas, dependências, registros de desenvolvimento e arquivos sem finalidade pública.
- O endereço e os caminhos do Pages continuem funcionando.
- As permissões e credenciais sejam limitadas ao necessário.

Pode configurar a origem do Pages como GitHub Actions, se necessário. Coordene essa alteração para não deixar a publicação atual sem atualização enquanto o PR aguarda revisão.

Não execute deployment manual da branch do PR nem publique suas mudanças antes do merge. Se alguma configuração depender de permissão indisponível, documente a pendência exata e informe o bloqueio.

## Documentação e registro do processo

Mantenha documentação versionada contendo:

- Visão geral do fluxo CI → CD → GitHub Pages.
- Ferramentas escolhidas e justificativa.
- Comandos de instalação e execução local.
- Verificações realizadas, páginas cobertas e critérios de erro versus aviso.
- Funcionamento da dependência entre os dois workflows.
- Configurações necessárias no GitHub e no Pages.
- Prompts e interações relevantes efetivamente utilizados.
- Resultados, problemas encontrados, correções e novas validações.
- Alterações feitas diretamente pelo agente e eventuais intervenções manuais do usuário.
- Evidências disponíveis, incluindo links para execuções do Actions e para o PR.
- Procedimento para validar o CD depois do merge.

Registre apenas fatos observados. Não invente prompts, falhas, intervenções, contagens ou evidências. Se o histórico disponível for parcial, declare essa limitação.

Diferencie claramente o que foi implementado, o que foi validado e o que permanece aguardando o merge.

## Execução e entrega

1. Inspecione o projeto, o enunciado e a configuração atual.
2. Implemente as ferramentas, verificações e os dois workflows.
3. Execute as validações locais e corrija os problemas encontrados.
4. Crie commits em uma branch própria, envie-a e abra um PR para `main`.
5. Acompanhe a CI do PR e corrija eventuais falhas até sua aprovação.
6. Deixe o PR aberto para revisão, sem merge e sem deployment antecipado.

Não crie agentes adicionais. Escolhas de ferramentas estão delegadas a você; alterações nas decisões de escopo exigem esclarecimento.

## Critérios de aceite

- Existem dois workflows separados, de CI e CD.
- CI configurada para push na `main` e PR para `main`.
- Lint e verificações de integridade cobrem o site inteiro.
- Todas as páginas HTML passam pelos testes automáticos de acessibilidade em desktop.
- Erros bloqueiam; avisos não.
- Indisponibilidade de links externos gera apenas avisos.
- Correções necessárias foram implementadas e documentadas.
