# apresentacaoPessoal

Site estático de apresentação pessoal, Projetos e GerminaFlix, vinculado a
[GustavoCostaAM/about-me](https://github.com/GustavoCostaAM/about-me).

Implementação em andamento da atividade **Lab CICD-Pipeline**. Os dois workflows
estão preparados, mas **a entrega ainda não está concluída nem pronta para merge**:
o ambiente do agente bloqueou instalação de dependências, geração do lock, escrita
em `.git` e acesso ao GitHub. O usuário informou uma CI com falha no PR 1; seus logs
não puderam ser lidos pelo agente. Falta resolver o lock e validar lint,
acessibilidade e CI. CD permanece aguardando o merge pelo usuário.

- [Configuração, ferramentas e operação](docs/ci-cd.md)
- [Registro factual do processo e validações](docs/processo.md)
- [Prompt da implementação](docs/prompts.md)

Após resolver as pendências de instalação descritas na documentação:

```sh
npm ci
npx playwright install --with-deps chromium
npm run test:integrity
npm test
```

Os testes de integridade e a montagem do site já podem ser executados sem pacotes
adicionais, com Python 3.11:

```sh
python tools/site.py build
python tools/site.py check
python -m unittest discover -s tools/tests -v
```

Nenhum deployment deve ser realizado da branch de desenvolvimento. O CD só será
validado depois do merge pelo proprietário.
