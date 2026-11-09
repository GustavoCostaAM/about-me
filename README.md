# apresentacaoPessoal

Site estático de apresentação pessoal, Projetos e GerminaFlix, vinculado a
[GustavoCostaAM/about-me](https://github.com/GustavoCostaAM/about-me).

Implementação em andamento da atividade **Lab CICD-Pipeline**. Os dois workflows
estão preparados. O lock agora está versionado; lint HTML/CSS, integridade das seis
páginas e dez testes do verificador passaram localmente. As correções da última
falha da CI ainda são locais: a próxima execução Linux precisa confirmar a
instalação do Chromium e a auditoria de acessibilidade. CD aguarda merge pelo usuário.

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

Depois de editar estilos, atualize os hashes SRI antes de validar e commitar:

```sh
npm run update:sri
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
