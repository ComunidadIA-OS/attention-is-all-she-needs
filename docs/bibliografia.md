<!--
SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
SPDX-License-Identifier: Apache-2.0
-->

# Bibliografía y Fuentes de Referencia
## Proyecto: «Attention Is All She Needs» (AIASN) — Reto «Mujeres por la IA Abierta»

> Este documento reúne el corpus bibliográfico, científico, metodológico, normativo y técnico que fundamenta la arquitectura, el diseño ético y la investigación de AIASN.  
> Las referencias se estructuran partiendo de las **fuentes fundamentales** sobre las que descansa el núcleo de la solución, seguidas de los bloques temáticos complementarios.

[← Volver al Índice de Documentación](./indice_de_documentacion.md) · [← Volver al README](../README.md)

---

## 1. Fuentes Fundamentales del Proyecto

Las siguientes obras constituyen los pilares teóricos, metodológicos y éticos sobre los que se formula y ejecuta AIASN:

### 1.1. Fundamentación Epistémica y Arquitectura Base
* **Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017).** *Attention Is All You Need*. In *Advances in Neural Information Processing Systems (NeurIPS 2017)* (Vol. 30, pp. 5998–6008). Curran Associates, Inc. [arXiv:1706.03762](https://arxiv.org/abs/1706.03762).  
  *Aportación clave:* Base fundacional del mecanismo de autoatención (*self-attention*) y de la arquitectura Transformer; resignificado en AIASN como el imperativo social y algorítmico de otorgar atención matemática y visibilidad a la voz experta de las mujeres en el espacio público.

### 1.2. Teoría Crítica de Medios y Métricas de Presencia
* **Tuchman, G. (1978).** The Symbolic Annihilation of Women by the Mass Media. In G. Tuchman, A. K. Daniels, & J. Walker (Eds.), *Hearth and Home: Images of Women in the Mass Media* (pp. 3–38). New York: Oxford University Press.  
  *Aportación clave:* Concepto rector de **«aniquilación simbólica»**: la invisibilización, condena o tratamiento testimonial de las mujeres en los medios como forma estructural de exclusión social y epistémica.
* **Kanter, R. M. (1977).** Some Effects of Proportions on Group Life: Skewed Sex Ratios and Responses to Token Women. *American Journal of Sociology*, 82(5), 965–990. [DOI: 10.1086/226425](https://doi.org/10.1086/226425).  
  *Aportación clave:* Teoría de la proporción crítica y del **«tokenismo»** (la trampa de la presencia cosmética o testimonial en minoría extrema); base sociológica de la regla anti-*equality-washing* de AIASN (alerta ante presencia física muda sin voz activa).
* **Bechdel, A. (1985).** *The Rule*. In *Dykes to Watch Out For*. Firebrand Books.  
  *Aportación clave:* Regla relacional de interacción entre mujeres en contenidos narrativos; adaptada formalmente en AIASN a la no ficción y al debate audiovisual mediante el **Test de Interlocución Femenina (TIF)** ([ADR-0011](./adr/0011-adopcion-test-interlocucion-femenina-tif.md)).

### 1.3. Ética Aplicada, Justicia y Cuidado
* **Cortina, A. (1986).** *Ética mínima: Introducción a la filosofía práctica*. Madrid: Tecnos.  
  *(Véase también Cortina, A., 1993, Ética aplicada y democracia radical, y 2007, Ética de la razón cordial).*  
  *Aportación clave:* Distinción entre **ética de mínimos** (justicia, equidad objetiva, paridad sustantiva exigible a todos) y **ética de máximos** (proyectos morales particulares); principio dialógico del **«interlocutor válido»**, que fundamenta la medición de la mujer como sujeto que aporta razones y no como mero objeto del discurso ajeno.
* **Gilligan, C. (1982).** *In a Different Voice: Psychological Theory and Women's Development*. Cambridge, MA: Harvard University Press. *(Ed. en español: Con otra voz, Barcelona: Icaria, 2023; y 2013, La ética del cuidado, Fundació Víctor Grífols i Lucas, n.º 30).*  
  *Aportación clave:* La **ética del cuidado** frente a las estructuras androcéntricas; fundamento para que AIASN no relegue temáticas de cuidado y conciliación a la periferia asistencial, sino a la gobernanza y sostenibilidad social.
* **Fraser, N. (1994 / 1997).** After the Family Wage: Gender Equity and the Welfare State. In *Justice Interruptus: Critical Reflections on the "Postsocialist" Condition* (pp. 41–66). New York: Routledge.  
  *Aportación clave:* El paradigma del **cuidador universal**, desmontando la asimetría laboral y la penalización profesional de las tareas de cuidado.

### 1.4. Sesgos Interseccionales en Inteligencia Artificial
* **Buolamwini, J., & Gebru, T. (2018).** Gender Shades: Intersectional Accuracy Disparities in Commercial Gender Classification. In *Proceedings of the 1st Conference on Fairness, Accountability and Transparency (PMLR)* (Vol. 81, pp. 77–91). [PMLR v81](https://proceedings.mlr.press/v81/buolamwini18a.html).  
  *Aportación clave:* Demostración empírica de tasas de error desproporcionadas en clasificadores biométricos comerciales ante mujeres y personas de piel oscura; justificación de la abstención ética ante $p < 0{,}80$, de la categoría `no_determinado` y del arbitraje humano preceptivo (*HitL*).
* **Bolukbasi, T., Chang, K.-W., Zou, J. Y., Saligrama, V., & Kalai, A. T. (2016).** Man Is to Computer Programmer as Woman Is to Homemaker? Debiasing Word Embeddings. In *Advances in Neural Information Processing Systems (NeurIPS 2016)* (Vol. 29, pp. 4349–4357). [arXiv:1607.06520](https://arxiv.org/abs/1607.06520).  
  *Aportación clave:* Demostración matemática de la captura y amplificación de estereotipos sexistas en representaciones vectoriales (*embeddings*); base del análisis semántico desacoplado en AIASN.

### 1.5. Aportaciones Formativas y Corpus del Reto (UPC / SEDIA / donesCOEINF)
* **Rodríguez Fonollosa, J. A. (2026).** *Taller de Habla: Transcripción, Diarización y Modelos Abiertos*. Secretaría de Estado de Digitalización e Inteligencia Artificial (SEDIA) y TALP-UPC.  
  *(Véase también el corpus de debate `Àgora` de TV3 / UPC, 36,9 horas de audio con Ground Truth manual del 14,61 % de habla femenina; y `Canal 3/24` de 87 horas).*
* **Vilaplana, V. (2026).** *Taller de Imagen y Vídeo: Detección, Reconocimiento Facial, Active Speaker y Tracking*. TALP-UPC y donesCOEINF.  
  *(Véase el baseline `baseline_CV_reto_VV.ipynb` y los hallazgos empíricos de la Diapositiva 91 sobre el sesgo del 50 % de mujeres clasificadas como `"unknown"` ante ángulos complejos).*
* **Gibert, K., & Gasch Pastor, Á. (2026).** *Sesiones de Perspectiva de Género, Ética e Inteligencia Artificial Confiable*. IDEAI-UPC, donesCOEINF y SEDIA.  
  *(Véase el Modelo PIO de la Cátedra OEIAC-UdG, la lista ALTAI, el modelo de gobernanza RIA y los proyectos de visibilidad de talento femenino `Top Rosies Talent`, `tFemTIC`, `ReDivIAcat` y `Quanta, quanta IA!`)*.
* **Guàrdia Güell, M. (2026).** *Sesión de Innovación Disruptiva, Viabilidad de Producto y Pitch*. Consell Social de la UPC y donesCOEINF.  
  *(Metodología de innovación en 4 pasos, diseño centrado en personas y validación ágil).*

---

## 2. Representación de Género en Medios Audiovisuales y Cultura

* **Aguilar, P. (varias).** *Mujer, amor y sexo en el cine español*. Madrid: Fundamentos. Análisis crítico de arquetipos y roles femeninos en el audiovisual español.
* **Arranz, F. (Dir.). (2010).** *Cine y género en España: Una investigación empírica*. Madrid: Cátedra. Estudio sociológico de la presencia femenina delante y detrás de las cámaras en la industria cinematográfica española.
* **CIMA — Asociación de Mujeres Cineastas y de Medios Audiovisuales. (2016–2025).** *Informes anuales sobre la representatividad de las mujeres en el sector cinematográfico y audiovisual español*. [CIMA Mujeres Cineastas](https://cimamujerescineastas.es/).
* **Collins, R. L. (2011).** Content Analysis of Gender Roles in Media: Where Are We Now and Where Should We Go? *Sex Roles*, 64(3–4), 290–298. [DOI: 10.1007/s11199-010-9929-5](https://doi.org/10.1007/s11199-010-9929-5).
* **de Lauretis, T. (1984).** *Alice Doesn't: Feminism, Semiotics, Cinema*. Bloomington: Indiana University Press.
* **de Lauretis, T. (1987).** *Technologies of Gender: Essays on Theory, Film, and Fiction*. Bloomington: Indiana University Press.
* **Gerbner, G., & Gross, L. (1976).** Living with Television: The Violence Profile. *Journal of Communication*, 26(2), 172–199. [DOI: 10.1111/j.1460-2466.1976.tb01397.x](https://doi.org/10.1111/j.1460-2466.1976.tb01397.x). *(Teoría del cultivo).*
* **Guarinos, V. (2009).** *Personajes femeninos en la ficción audiovisual*. Sevilla: Universidad de Sevilla.
* **Haskell, M. (1974).** *From Reverence to Rape: The Treatment of Women in the Movies*. New York: Holt, Rinehart and Winston.
* **hooks, b. (1992).** The Oppositional Gaze: Black Female Spectators. In *Black Looks: Race and Representation* (pp. 115–131). Boston: South End Press.
* **Kaplan, E. A. (1983).** *Women and Film: Both Sides of the Camera*. New York: Methuen.
* **Kuhn, A. (1982).** *Women's Pictures: Feminism and Cinema*. London: Routledge & Kegan Paul.
* **Lacalle, C. (2013).** *Jóvenes y ficción televisiva: Construcción de identidad y transmedialidad*. Barcelona: UOC Press. *(Y estudios longitudinales sobre mujeres en ficción televisiva)*.
* **Lauzen, M. M. (2000–2025).** *The Celluloid Ceiling: Employment of Behind-the-Scenes Women on Top Grossing U.S. Films* y *Boxed In: Women On Screen and Behind the Scenes in Television*. Center for the Study of Women in Television and Film, San Diego State University (SDSU). [SDSU Women in TV & Film](https://womenintvfilm.sdsu.edu/).
* **Macharia, S. et al. / WACC. (2020).** *Who Makes the News? 6th Global Media Monitoring Project (GMMP)*. Toronto: World Association for Christian Communication. [GMMP 2020](https://whomakesthenews.org/).
* **Mulvey, L. (1975).** Visual Pleasure and Narrative Cinema. *Screen*, 16(3), 6–18. [DOI: 10.1093/screen/16.3.6](https://doi.org/10.1093/screen/16.3.6). *(La mirada masculina / male gaze)*.
* **Signorielli, N. (1989).** Television and Conceptions about Vulnerability: The Other Face of the Mean World Syndrome. *Journal of Broadcasting & Electronic Media*, 33(3), 325–331.
* **Smith, S. L., Choueiti, M., & Pieper, K. (2010–2025).** *Inequality in Popular Films: Examining Gender, Race/Ethnicity, LGBTQ+ and Disability on Screen and Behind the Camera*. USC Annenberg Inclusion Initiative. [USC Annenberg](https://annenberg.usc.edu/research/aii).

---

## 3. Procesamiento de Lenguaje Natural, Diálogo y Sesgo en Embeddings

* **Agarwal, A., Zheng, J., Kamath, S., Balasubramanian, S., & Dey, S. A. (2015).** Key Female Characters in Film Have More to Talk About Besides Men: Automating the Bechdel Test on Screenplays. In *Proceedings of the 2015 Conference of the North American Chapter of the ACL: Human Language Technologies* (pp. 830–840). [ACL Anthology](https://aclanthology.org/N15-1084/).
* **Caliskan, A., Bryson, J. J., & Narayanan, A. (2017).** Semantics Derived Automatically from Language Corpora Contain Human-like Biases. *Science*, 356(6334), 183–186. [DOI: 10.1126/science.aal4230](https://doi.org/10.1126/science.aal4230). *(Test WEAT — Word Embedding Association Test)*.
* **Ethayarajh, K., Duvenaud, D., & Hirst, G. (2019).** Understanding Undesirable Word Embedding Associations. In *Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics (ACL 2019)* (pp. 1696–1705). [ACL Anthology](https://aclanthology.org/P19-1166/).
* **Garg, N., Schiebinger, L., Jurafsky, D., & Zou, J. (2018).** Word Embeddings Quantify 100 Years of Gender and Ethnic Stereotypes. *Proceedings of the National Academy of Sciences (PNAS)*, 115(16), E3635–E3644. [DOI: 10.1073/pnas.1720347115](https://doi.org/10.1073/pnas.1720347115).
* **Gonen, H., & Goldberg, Y. (2019).** Lipstick on a Pig: Debiasing Methods Cover up Systematic Gender Biases in Word Embeddings But Do Not Remove Them. In *Proceedings of the 2019 Conference of the NAACL: HLT* (pp. 609–614). [arXiv:1903.03862](https://arxiv.org/abs/1903.03862).
* **Gutiérrez-Fandiño, A., Armengol-Estapé, J., de Gibert Bonet, O., & Villegas, M. (2022).** MarIA: Spanish Language Models. *Procesamiento del Lenguaje Natural*, 68, 39–60. [PLN Revista](http://journal.sepln.org/sepln/ojs/index.php/pln/article/view/6417).
* **Martinez, V. R., Somandepalli, K., & Narayanan, S. (2022).** Boys Don't Cry (or Kiss or Dance): A Computational Linguistic Lens into Gendered Actions in Film. *PLOS ONE*, 17(11), e0278604. [DOI: 10.1371/journal.pone.0278604](https://doi.org/10.1371/journal.pone.0278604).
* **Ramakrishna, A., Martinez, V. R., Malandrakis, N., Singla, K., & Narayanan, S. (2017).** Linguistic Analysis of Differences in Portrayal of Movie Characters. In *Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing (EMNLP)* (pp. 1669–1678). [ACL Anthology](https://aclanthology.org/D17-1176/).
* **Sap, M., Prasettio, M. C., Holtzman, A., Rashkin, H., & Choi, Y. (2017).** Connotation Frames of Power and Agency in Modern Films. In *Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing (EMNLP)* (pp. 2329–2334). [ACL Anthology](https://aclanthology.org/D17-1247/).
* **Tripodi, F. (2021).** Ms. Categorized: Gender, Qualification, and Wikipedia's Notability Guidelines. *New Media & Society*, 25(7), 1687–1707. [DOI: 10.1177/14614448211023772](https://doi.org/10.1177/14614448211023772).
* **Wagner, C., Garcia, D., Jadidi, M., & Strohmaier, M. (2015).** It's a Man's Wikipedia? Assessing Gender Inequality in an Online Encyclopedia. In *Ninth International AAAI Conference on Web and Social Media (ICWSM 2015)*. [arXiv:1501.06307](https://arxiv.org/abs/1501.06307).
* **Zhao, J., Wang, T., Yatskar, M., Ordonez, V., & Chang, K.-W. (2017).** Men Also Like Shopping: Reducing Gender Bias Amplification using Corpus-level Constraints. In *Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing (EMNLP)* (pp. 2979–2989). [arXiv:1707.09457](https://arxiv.org/abs/1707.09457).
* **Zhou, P., Shi, W., Zhao, J., Huang, K.-H., Chen, M., Ryan, P., & Chang, K.-W. (2019).** Examining Gender Bias in Languages with Grammatical Gender. In *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP)* (pp. 5276–5284). [ACL Anthology](https://aclanthology.org/D19-1531/).

---

## 4. Sistemas Computacionales Multimodales y Análisis Audiovisual

* **Bamman, D., Samberg, R., So, R. J., & Zhou, N. (2024).** Measuring Diversity in Hollywood through the Large-Scale Computational Analysis of Film. *Proceedings of the National Academy of Sciences (PNAS)*, 121(34), e2409770121. [DOI: 10.1073/pnas.2409770121](https://doi.org/10.1073/pnas.2409770121).
* **Geena Davis Institute on Gender in Media, USC SAIL, & Google Research. (2023).** *Reflecting India: An Intersectional and Longitudinal Analysis of Representation in Indian Popular Television*. [Informe en PDF](https://geenadavisinstitute.org/wp-content/uploads/2024/01/2023-GDI-Reflecting-India-Study.pdf).
* **Guha, T., Huang, C.-W., Kumar, N., Zhu, Y., & Narayanan, S. S. (2015).** Gender Representation in Cinematic Content: A Multimodal Approach. In *Proceedings of the 2015 ACM on International Conference on Multimodal Interaction (ICMI '15)* (pp. 31–34). [DOI: 10.1145/2818346.2820778](https://doi.org/10.1145/2818346.2820778). *(Base técnica de la herramienta GD-IQ)*.
* **Hong, J., Crichton, W., Zhang, H., Fu, D. Y., Bradbury, J., & Fatahalian, K. (2021).** Analysis of Faces in a Decade of US Cable TV News. In *Proceedings of the 27th ACM SIGKDD Conference on Knowledge Discovery & Data Mining* (pp. 3025–3035). [ACM Digital Library](https://dl.acm.org/doi/10.1145/3447548.3467147). *(Stanford Cable TV News Analyzer)*.
* **Jang, J. Y., Baek, S., & Baik, S. (2019).** Quantification of Gender Representation Bias in Commercial Films based on Image Analysis. In *Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV) Workshops*.
* **Mazières, A., Menezes, T., & Roth, C. (2021).** Computational Appraisal of Gender Representativeness in Popular Films. *Humanities and Social Sciences Communications*, 8(1), 1–11. [DOI: 10.1057/s41599-021-00815-9](https://doi.org/10.1057/s41599-021-00815-9).
* **Sassatelli, D., Hu, X., & TRACTIVE Consortium. (2025).** MObyGaze: A Film Dataset of Multimodal Objectification Densely Annotated by Experts. *arXiv preprint*. [arXiv:2505.22084](https://arxiv.org/abs/2505.22084).
* **Scheuerman, M. K., Paul, J. M., & Brubaker, J. R. (2019).** How Computers See Gender: An Evaluation of Gender Classification in Commercial Facial Analysis and Image Labeling Services. *Proceedings of the ACM on Human-Computer Interaction*, 3(CSCW), Article 144. [DOI: 10.1145/3359246](https://doi.org/10.1145/3359246).
* **Somandepalli, K., Guha, T., Martinez, V. R., Kumar, N., Hartvigsen, H., & Narayanan, S. (2021).** Computational Media Intelligence: Human-Centered Machine Analysis of Media. *Proceedings of the IEEE*, 109(5), 891–910. [DOI: 10.1109/JPROC.2020.3045610](https://doi.org/10.1109/JPROC.2020.3045610).

---

## 5. Ética, Filosofía, Teoría Social y Epistemología

* **Barrett, L. F., Adolphs, R., Marsella, S., Martinez, A. M., & Pollak, S. D. (2019).** Emotional Expressions Reconsidered: Challenges to Inferring Emotion From Human Facial Movements. *Psychological Science in the Public Interest*, 20(1), 1–68. [DOI: 10.1177/1529100619832930](https://doi.org/10.1177/1529100619832930). *(Evidencia científica sobre los límites del reconocimiento facial de emociones; base de ADR-0009).*
* **Benkler, Y. (2006).** *The Wealth of Networks: How Social Production Transforms Markets and Freedom*. New Haven, CT: Yale University Press. *(Ed. en español: La riqueza de las redes, Barcelona: Icaria, 2015).*
* **Carrasco Bengoa, C. (Ed.). (2011).** *El trabajo de cuidados: Historia, teoría y políticas*. Madrid: Catarata.
* **Estés, C. P. (1992).** *Women Who Run with the Wolves: Myths and Stories of the Wild Woman Archetype*. New York: Ballantine Books. *(Ed. en español: Mujeres que corren con los lobos, Barcelona: Ediciones B, 1998; comentada en la sesión formativa por Karina Gibert).*
* **Haraway, D. (1988).** Situated Knowledges: The Science Question in Feminism and the Privilege of Partial Perspective. *Feminist Studies*, 14(3), 575–599. [DOI: 10.2307/3178066](https://doi.org/10.2307/3178066).
* **Hirschman, A. O. (1970).** *Exit, Voice, and Loyalty: Responses to Decline in Firms, Organizations, and States*. Cambridge, MA: Harvard University Press. *(Ed. en español: Salida, voz y lealtad, México: Fondo de Cultura Económica, 1977).*
* **Lugones, M. (2008).** Colonialidad y género. *Tabula Rasa*, 9, 73–101.
* **Lugones, M. (2010).** Toward a Decolonial Feminism. *Hypatia: A Journal of Feminist Philosophy*, 25(4), 742–759. [DOI: 10.1111/j.1527-2001.2010.01137.x](https://doi.org/10.1111/j.1527-2001.2010.01137.x).
* **Mohanty, C. T. (2003).** *Feminism without Borders: Decolonizing Theory, Practicing Solidarity*. Durham, NC: Duke University Press.
* **Ostrom, E., & Hess, C. (Eds.). (2007).** *Understanding Knowledge as a Commons: From Theory to Practice*. Cambridge, MA: MIT Press.
* **Pérez Orozco, A. (2014).** *Subversión feminista de la economía: Aportes para un debate sobre el conflicto capital-vida*. Madrid: Traficantes de Sueños.
* **Spivak, G. C. (1988).** Can the Subaltern Speak? In C. Nelson & L. Grossberg (Eds.), *Marxism and the Interpretation of Culture* (pp. 271–313). Urbana: University of Illinois Press.
* **Tiebout, C. M. (1956).** A Pure Theory of Local Expenditures. *Journal of Political Economy*, 64(5), 416–424. [DOI: 10.1086/257839](https://doi.org/10.1086/257839). *(Base del principio de «votar con los pies y con la confianza»).*

---

## 6. Marco Normativo, Regulatorio y Estándares Oficiales

### Unión Europea
* **Reglamento (UE) 2024/1689 del Parlamento Europeo y del Consejo**, de 13 de junio de 2024, por el que se establecen normas armonizadas en materia de inteligencia artificial (*Reglamento Europeo de IA — RIA*). DOUE L 2024/1689. [EUR-Lex](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689). *(Arts. 5, 14, 50 y Anexo III).*
* **Comisión Europea. (2025).** *Directrices de la Comisión sobre la aplicación del artículo 50 del Reglamento Europeo de IA (Transparencia e IA Generativa)*. C(2025) 5054 final.
* **Comisión Europea. (2025).** *Directrices relativas a las prácticas de IA prohibidas en virtud del artículo 5 del Reglamento de IA*. C(2025) 884 final.
* **Directiva (UE) 2022/2464**, sobre presentación de información sobre sostenibilidad por parte de las empresas (*CSRD*) y estándares europeos de información sobre sostenibilidad **ESRS S1** (*Own Workforce*).
* **Directiva (UE) 2023/970**, por la que se refuerza la aplicación del principio de igualdad de retribución entre hombres y mujeres a través de medidas de transparencia retributiva.
* **Directiva (UE) 2024/825**, por la que se modifican las Directivas 2005/29/CE y 2011/83/UE en lo que respecta al empoderamiento de los consumidores para la transición ecológica frente a prácticas desleales (*Anti-Equality Washing / Greenwashing*).
* **Reglamento (UE) 2016/679 (*RGPD*)**, relativo a la protección de las personas físicas en lo que respecta al tratamiento de datos personales y a la libre circulación de estos datos. *(Arts. 4.14, 5.1.c y 9).*
* **Directiva (UE) 2019/882**, sobre los requisitos de accesibilidad de los productos y servicios (*European Accessibility Act*).
* **High-Level Expert Group on AI (AI HLEG). (2019).** *Ethics Guidelines for Trustworthy Artificial Intelligence* (Evaluación ALTAI). Bruselas: Comisión Europea.
* **Declaración Europea sobre los Derechos y Principios Digitales para la Década Digital (2023/C 23/01)**. DOUE C 23, de 23 de enero de 2023.

### España
* **Ley Orgánica 2/2024, de 1 de agosto**, de representación paritaria y presencia equilibrada de mujeres y hombres. BOE núm. 186, de 02/08/2024.
* **Ley Orgánica 3/2007, de 22 de marzo**, para la igualdad efectiva de mujeres y hombres. BOE núm. 71, de 23/03/2007. *(Arts. 14, 36, 37 y 41).*
* **Ley 13/2022, de 7 de julio**, General de Comunicación Audiovisual. BOE núm. 163, de 08/07/2022.
* **Real Decreto-ley 24/2021, de 2 de noviembre**, de transposición de directivas de la Unión Europea en materia de derechos de autor y derechos afines en el mercado único digital. BOE núm. 263, de 03/11/2021. *(Art. 67: Excepción legal para minería de textos y datos — TDM).*
* **Ley 2/2023, de 20 de febrero**, reguladora de la protección de las personas que informen sobre infracciones normativas y de lucha contra la corrupción (*Ley de Whistleblowing*).
* **Comisión Nacional del Mercado de Valores (CNMV). (2024 / 2025).** *Informe sobre las juntas generales de accionistas y comisiones de retribuciones de las sociedades cotizadas* y estadísticas anuales de consejeras en el IBEX 35.
* **Norma UNE 153101:2018 EX.** *Lectura Fácil: Pautas y recomendaciones para la elaboración de documentos*. Madrid: Asociación Española de Normalización (UNE).

---

## 7. Modelos de IA Abierta y Tecnologías del Pipeline

* **Baek, Y., Lee, B., Han, D., Yun, S., & Lee, H. (2019).** Character Region Awareness for Text Detection (CRAFT). In *CVPR 2019* (pp. 9365–9374). [CRAFT Text Detector](https://github.com/clovaai/CRAFT-pytorch). *(Motor OCR subyacente de EasyOCR, JaidedAI)*.
* **Deng, J., Guo, J., Xue, N., & Zafeiriou, S. (2019).** ArcFace: Additive Angular Margin Loss for Deep Face Recognition. In *CVPR 2019* (pp. 4690–4699). [InsightFace](https://github.com/deepinsight/insightface). *(Pesos `buffalo_l` para re-identificación en RAM)*.
* **Ge, Z., Liu, S., Wang, F., Li, Z., & Sun, J. (2021).** YOLOX: Exceeding YOLO Series in 2021. *arXiv preprint*. [arXiv:2107.08430](https://arxiv.org/abs/2107.08430). *(Adaptador permisivo Apache-2.0 de la hoja de ruta)*.
* **Kuprashevich, M., & Chernukhina, I. (2023).** MiVOLO: Multi-input Transformer for Age and Gender Estimation. *arXiv preprint*. [arXiv:2307.04616](https://arxiv.org/abs/2307.04616).
* **Open Source Initiative (OSI). (2024).** *The Open Source AI Definition (OSAID v1.0)*. [opensource.org/ai](https://opensource.org/ai).
* **Nygard, M. (2011).** *Documenting Architecture Decisions*. Cognitect Blog. *(Metodología estándar ADR adoptada en AIASN)*.
* **Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2022).** Robust Speech Recognition via Large-Scale Weak Supervision. *arXiv preprint*. [arXiv:2212.04356](https://arxiv.org/abs/2212.04356). *(Whisper large v3 en OVHcloud AI Endpoints)*.
* **Souček, T., & Lokoč, J. (2020).** TransNet V2: An Effective Deep Network for Fast Shot Transition Detection. *arXiv preprint*. [arXiv:2008.04838](https://arxiv.org/abs/2008.04838).
* **Tao, R., Pan, Z., Das, R. K., Qian, X., Fallon, M. Z., & Li, H. (2021).** Is Someone Speaking? Exploring Extreme Length Input for Active Speaker Detection. In *ACM MM 2021* (pp. 3927–3935). *(TalkNet-ASD para detector de hablante activo)*.
* **Touvron, H. et al. / Meta AI. (2024).** *The Llama 3 Herd of Models*. *arXiv preprint*. [arXiv:2407.21783](https://arxiv.org/abs/2407.21783). *(Llama 3.3 70B Instruct en OVHcloud AI Endpoints)*.
* **Ultralytics. (2024).** *YOLO11m: Real-Time Object Detection and Pose Estimation*. [GitHub Ultralytics](https://github.com/ultralytics/ultralytics).
* **Xiao, S. et al. / BAAI. (2024).** *C-Pack: Packaged Resources to Advance General Chinese Embedding*. *(Modelo BGE-M3 para embeddings multilingües)*.
