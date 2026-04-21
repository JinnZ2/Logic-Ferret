# Logic-Ferret integrations subpackage.
#
# Adapters that pair Ferret's text analysis with sibling frameworks'
# numerical/structural outputs. Each adapter is standalone -- no
# runtime imports from the sibling repos; only shape references if any.
#
# v0 contents:
#   - financial_text: scans financial/investment text against
#     Ferret's sensors plus financial-specific inversion markers.
#     Designed to cross-reference with metabolic-accounting's
#     money_signal/ and investment_signal/ modules when a consumer
#     has built that context.
