# Google Gemini API Model adapters

This repository contains the code for Dataloop model adapters that invoke Google Gemini models, such as Gemini Pro, Gemini Flash, and others, served via API.

More information on Google Gemini can be found [here](https://ai.google.dev/gemini-api/docs).

### Using Google Gemini Models in Dataloop Platform

- To get a Google Gemini API Key, follow the instructions on the [Google AI for Developers](https://ai.google.dev/gemini-api/docs/api-key) website.
- Install the model from the [Dataloop Marketplace](https://docs.dataloop.ai/docs/marketplace)
- Add the API Key as a Secret to your organization's [Data Governance](https://docs.dataloop.ai/docs/overview-1?highlight=data%20governance)
- Add the secret to the model's [service configuration](https://docs.dataloop.ai/docs/service-runtime#secrets-for-faas)

### Important Note on Google Gemini Model Usage

While the adapter code in this repository is open-sourced under the Apache License 2.0, users of Google Gemini models must adhere to Google's terms and policies:

- [Google APIs Terms of Service](https://developers.google.com/terms)
- [Gemini API Additional Terms of Service](https://ai.google.dev/gemini-api/terms)

By using Google Gemini models, you acknowledge and agree to comply with these terms.

For any questions regarding the usage or licensing of Google Gemini models, please refer to the [Google AI for Developers documentation](https://ai.google.dev/gemini-api/docs/models).

---
