from tests.plugins.duel import DuelTestCase


class Test_plugin(DuelTestCase):

    def test_duel_propose_self(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.clearMessageHistory()
        self.mike.says('!duel mike')
        # THEN
        self.assertListEqual(['You cannot duel yourself!'], self.mike.message_history)

    def test_duel_propose_with_valid_client(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.clearMessageHistory()
        self.bill.clearMessageHistory()
        self.mike.says('!duel bill')
        # THEN
        self.assertListEqual(['Mike proposes a duel: to accept type !duel mike'], self.bill.message_history)
        self.assertListEqual(['Duel proposed to Bill'], self.mike.message_history)

    def test_duel_propose_with_valid_client_and_accept(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.clearMessageHistory()
        self.bill.clearMessageHistory()
        self.mike.says('!duel bill')
        self.bill.says('!duel mike')
        # THEN
        self.assertListEqual(["Mike proposes a duel: to accept type !duel mike",
                              "You accepted Mike's duel",
                              "[Duel]: Bill 0:0 Mike"], self.bill.message_history)
        self.assertListEqual(["Duel proposed to Bill",
                              "Bill is now duelling with you",
                              "[Duel]: Mike 0:0 Bill"], self.mike.message_history)

    def test_duelreset_with_no_duel(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.clearMessageHistory()
        self.mike.says('!duelreset bill')
        # THEN
        self.assertListEqual(['You have no duel in progress: nothing to reset!'], self.mike.message_history)

    def test_duelreset_with_invalid_duel_handle(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.says('!duel bill')
        self.bill.says('!duel mike')
        self.mike.clearMessageHistory()
        self.bill.clearMessageHistory()
        self.mike.says('!duelreset anna')
        # THEN
        self.assertListEqual(['You have no duel with Anna: cannot reset!'], self.mike.message_history)

    def test_duelreset_with_multiple_duel_and_no_handle(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.says('!duel bill')
        self.mike.says('!duel anna')
        self.bill.says('!duel mike')
        self.anna.says('!duel mike')
        self.mike.clearMessageHistory()
        self.bill.clearMessageHistory()
        self.anna.clearMessageHistory()
        self.mike.says('!duelreset')
        # THEN
        self.assertListEqual(['You have 2 duels running, type !duelreset <name>'], self.mike.message_history)

    def test_duelreset_with_multiple_duel_and_handle_given(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.says('!duel bill')
        self.mike.says('!duel anna')
        self.bill.says('!duel mike')
        self.anna.says('!duel mike')
        self.mike.clearMessageHistory()
        self.bill.clearMessageHistory()
        self.anna.clearMessageHistory()
        self.mike.says('!duelreset anna')
        # THEN
        self.assertListEqual(['[Duel]: Mike 0:0 Anna'], self.mike.message_history)
        self.assertListEqual(['[Duel]: Anna 0:0 Mike'], self.anna.message_history)

    def test_duelcancel_with_no_duel(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.clearMessageHistory()
        self.mike.says('!duelcancel bill')
        # THEN
        self.assertListEqual(['You have no duel in progress: nothing to cancel!'], self.mike.message_history)

    def test_duelcancel_with_invalid_duel_handle(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.says('!duel bill')
        self.bill.says('!duel mike')
        self.mike.clearMessageHistory()
        self.bill.clearMessageHistory()
        self.mike.says('!duelcancel anna')
        # THEN
        self.assertListEqual(['You have no duel with Anna: cannot cancel!'], self.mike.message_history)

    def test_duelcancel_with_multiple_duel_and_no_handle(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.says('!duel bill')
        self.mike.says('!duel anna')
        self.bill.says('!duel mike')
        self.anna.says('!duel mike')
        self.mike.clearMessageHistory()
        self.bill.clearMessageHistory()
        self.anna.clearMessageHistory()
        self.mike.says('!duelcancel')
        # THEN
        self.assertListEqual(['You have 2 duels running, type !duelcancel <name>'], self.mike.message_history)

    def test_duelcancel_with_multiple_duel_and_handle_given(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.says('!duel bill')
        self.mike.says('!duel anna')
        self.bill.says('!duel mike')
        self.anna.says('!duel mike')
        self.mike.clearMessageHistory()
        self.bill.clearMessageHistory()
        self.anna.clearMessageHistory()
        self.mike.says('!duelcancel anna')
        # THEN
        self.assertListEqual(['Duel with Anna canceled'], self.mike.message_history)
        self.assertListEqual(['Duel with Mike canceled'], self.anna.message_history)
        self.assertEqual(1, len(self.mike.var(self.p, 'duelling', {}).value))
        self.assertEqual(0, len(self.anna.var(self.p, 'duelling', {}).value))
        self.assertEqual(1, len(self.bill.var(self.p, 'duelling', {}).value))

    def test_duelaction(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.says('!duel bill')
        self.mike.says('!duel anna')
        self.bill.says('!duel mike')
        self.anna.says('!duel mike')
        self.mike.clearMessageHistory()
        self.bill.clearMessageHistory()
        self.anna.clearMessageHistory()
        self.console.queueEvent(self.console.getEvent('EVT_CLIENT_KILL', client=self.mike, target=self.anna))
        self.console.queueEvent(self.console.getEvent('EVT_CLIENT_KILL', client=self.mike, target=self.anna))
        self.console.queueEvent(self.console.getEvent('EVT_CLIENT_KILL', client=self.mike, target=self.bill))
        self.console.queueEvent(self.console.getEvent('EVT_CLIENT_KILL', client=self.bill, target=self.mike))
        self.console.queueEvent(self.console.getEvent('EVT_CLIENT_KILL', client=self.bill, target=self.anna))
        self.mike.says('!duelreset anna')
        self.mike.says('!duelcancel bill')
        # THEN
        self.assertListEqual(['[Duel]: Mike 1:0 Anna',
                              '[Duel]: Mike 2:0 Anna',
                              '[Duel]: Mike 1:0 Bill',
                              '[Duel]: Mike 1:1 Bill',
                              '[Duel]: Mike 0:0 Anna',
                              'Duel with Bill canceled'], self.mike.message_history)
        self.assertListEqual(['[Duel]: Anna 0:1 Mike',
                              '[Duel]: Anna 0:2 Mike',
                              '[Duel]: Anna 0:0 Mike'], self.anna.message_history)
        self.assertListEqual(['[Duel]: Bill 0:1 Mike',
                              '[Duel]: Bill 1:1 Mike',
                              'Duel with Mike canceled'], self.bill.message_history)


    def test_event_client_disconnect_with_active_duel(self):
        # GIVEN
        self.mike.connects("1")
        self.bill.connects("2")
        self.anna.connects("3")
        # WHEN
        self.mike.says('!duel bill')
        self.mike.says('!duel anna')
        self.bill.says('!duel mike')
        self.anna.says('!duel mike')
        self.console.queueEvent(self.console.getEvent('EVT_CLIENT_KILL', client=self.mike, target=self.anna))
        self.console.queueEvent(self.console.getEvent('EVT_CLIENT_KILL', client=self.mike, target=self.anna))
        self.console.queueEvent(self.console.getEvent('EVT_CLIENT_KILL', client=self.mike, target=self.bill))
        self.console.queueEvent(self.console.getEvent('EVT_CLIENT_KILL', client=self.bill, target=self.mike))
        self.console.queueEvent(self.console.getEvent('EVT_CLIENT_KILL', client=self.bill, target=self.anna))
        self.mike.clearMessageHistory()
        self.bill.clearMessageHistory()
        self.anna.clearMessageHistory()
        self.console.queueEvent(self.console.getEvent('EVT_CLIENT_DISCONNECT', client=self.mike))
        # THEN
        self.assertListEqual(['[Duel]: Anna 0:2 Mike', 'Duel with Mike canceled'], self.anna.message_history)
        self.assertListEqual(['[Duel]: Bill 1:1 Mike', 'Duel with Mike canceled'], self.bill.message_history)
        self.assertEqual(0, len(self.anna.var(self.p, 'duelling', {}).value))
        self.assertEqual(0, len(self.bill.var(self.p, 'duelling', {}).value))
