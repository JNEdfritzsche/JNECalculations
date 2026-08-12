
def get_nec_transformer_protection_flowchart():
    return r"""
    digraph G {
        rankdir=TB;
        
        node [shape=ellipse, style=rounded];
        n_rating [label="Rating"];
        
        node [shape=diamond, fixedsize=true, width=1.5, height=1.0];
        n1_loc [label="Location\nLimitations"];
        n1_1_z [label="TX\nImpedance"];
        n1_1_1_v_sec [label="Secondary\nVoltage"];
        n1_1_2_v_sec [label="Secondary\nVoltage"];          
        n1_2_prot [label="Protection\nMethod"];
        n1_2_2_z [label="TX\nImpedance"];
        n1_2_2_1_v_sec [label="Secondary\nVoltage"];
        n1_2_2_2_v_sec [label="Secondary\nVoltage"];
        n2_prot [label="Protection\nMethod"];
        n2_1_flc [label="Primary\nFLC"];
        n2_2_flc [label="Secondary\nFLC"];
        
        {
            node [shape=box, style=rounded];
            
            n1_1_1_1_out [label="Primary:\nCB: 600% / FR: 300%\nSecondary:\nCB: 300% / FR: 250%"];
            n1_1_1_2_out [label="Primary:\nCB: 600% / FR: 300%\nSecondary:\nCB/FR: 125%"];
            n1_1_2_1_out [label="Primary:\nCB: 400% / FR: 300%\nSecondary:\nCB: 250% / FR: 225%"];
            n1_1_2_2_out [label="Primary:\nCB: 400% / FR: 300%\nSecondary:\nCB/FR: 125%"];
            n1_2_1_out [label="Primary:\nCB: 300% / FR: 250%\nSecondary:\nNot required"];
            n1_2_2_1_1_out [label="Primary:\nCB: 600% / FR: 300%\nSecondary:\nCB: 300% / FR: 250%"];
            n1_2_2_1_2_out [label="Primary:\nCB: 600% / FR: 300%\nSecondary:\nCB/FR: 250%"];
            n1_2_2_2_1_out [label="Primary:\nCB: 400% / FR: 300%\nSecondary:\nCB: 250% / FR: 225%"];
            n1_2_2_2_2_out [label="Primary:\nCB:  400% / FR: 300%\nSecondary:\nCB/FR: 250%"];
            n2_1_1_out [label="Primary:\nCB/FR: 125%\nSecondary:\nNot required"];
            n2_1_2_out [label="Primary:\nCB/FR: 167%\nSecondary:\nNot required"];
            n2_1_3_out [label="Primary:\nCB/FR: 300%\nSecondary:\nNot required"];
            n2_2_1_out [label="Primary:\nCB/FR: 250%\nSecondary:\nCB/FR: 125%"];
            n2_2_2_out [label="Primary:\nCB/FR: 250%\nSecondary:\nCB/FR: 167%"];
        }
        
        edge [arrowsize=0.75];
        n_rating -> n1_loc [label="> 1000 V"];
            n1_loc -> n1_1_z [label="Any location"];
                n1_1_z -> n1_1_1_v_sec [label="Z <= 6%"];
                    n1_1_1_v_sec -> n1_1_1_1_out [label="> 1000 V"];
                    n1_1_1_v_sec -> n1_1_1_2_out [label="<= 1000 V"];
                n1_1_z -> n1_1_2_v_sec [label="6% < Z <= 10%"];
                    n1_1_2_v_sec -> n1_1_2_1_out [label="> 1000 V"];
                    n1_1_2_v_sec -> n1_1_2_2_out [label="<= 1000 V"];
            n1_loc -> n1_2_prot [label="Supervised location"];
                n1_2_prot -> n1_2_1_out [label="Pri. only"];
                n1_2_prot -> n1_2_2_z [label="P&S"];
                    n1_2_2_z -> n1_2_2_1_v_sec [label="Z <= 6%"];
                        n1_2_2_1_v_sec -> n1_2_2_1_1_out [label="> 1000 V"];
                        n1_2_2_1_v_sec -> n1_2_2_1_2_out [label="<= 1000 V"];
                    n1_2_2_z -> n1_2_2_2_v_sec [label="6% < Z <= 10%"];
                        n1_2_2_2_v_sec -> n1_2_2_2_1_out [label="> 1000 V"];
                        n1_2_2_2_v_sec -> n1_2_2_2_2_out [label="<= 1000 V"];
        n_rating -> n2_prot [label="<= 1000 V"];
            n2_prot -> n2_1_flc [label="FLC"];
                n2_1_flc -> n2_1_1_out [label="I >= 9A"];
                n2_1_flc -> n2_1_2_out [label="2 <= I < 9A"];
                n2_1_flc -> n2_1_3_out [label="I < 2A"];
            n2_prot -> n2_2_flc [label="P&S"];
                n2_2_flc -> n2_2_1_out [label="I >= 9A"];
                n2_2_flc -> n2_2_2_out [label="I < 9A"];
    }
    """


def get_oesc_transformer_protection_flowchart():
    return """
    digraph G {
      rankdir=TB;
      node [shape=box, style=rounded];

      d1 [label="Rating "];
      d1 -> d2 [taillabel="> 750V", labeldistance=4, labelfontsize=10];
      d2 [label="Protection level", shape=diamond, fixedsize = true, width=1.2, height=0.8, margin=0.05];
      d2 -> d3 [label="", taillabel="P & S", labeldistance=5, labelfontsize=10];
      d3 [label="Impedance", shape=diamond, fixedsize = true, width=1.2, height=0.8, margin=0.05];
      d5 [label="CB: 300%\nF:150%"];
      d2 -> d5 [label= "Pri.\nonly"];
      d6 [label="For side", shape=diamond, fixedsize = true, width=1.2, height=0.8, margin=0.05];
      d7 [label="For side", shape=diamond, fixedsize = true, width=1.2, height=0.8, margin=0.05];
      d3 -> d6 [taillabel="Z <= 7.5%", labeldistance=7, labelfontsize=10];
      d3 -> d7 [label="7.5% < Z <= 10%"];
      d8 [label="CB: 600%\nF:300%"];
      d9 [label="Voltage", shape=diamond, fixedsize = true, width=1.2, height=0.8, margin=0.05];
      d10 [label="Voltage", shape=diamond, fixedsize = true, width=1.2, height=0.8, margin=0.05];
      d6 -> d8 [taillabel="Pri. >750V", labeldistance=5, labelfontsize=10];
      d6 -> d9 [label="Sec."];
      d7 -> d10 [label="Sec."];
      d7 -> d11 [label="Pri. >750V"];
      d11 [label="CB: 400%\nF:200%"];
      d12 [label="CB:300%\nF:150%"];
      d13 [label="CB:250%\nF:250%"];
      d14 [label="CB:250%\nF:125%"];
      d9 -> d12 [label=">750V"];
      d9 -> d13 [label ="<=750V"];
      d10 -> d13 [label="<=750V"];
      d10 -> d14 [label=">750V"];

      d15 [label ="Insulation", shape=diamond, fixedsize = true, width=1.2, height=0.8, margin=0.05];
      d16 [label ="Protection \nlevel", shape=diamond, fixedsize = true, width=1.2, height=0.8, margin=0.05];
      d17 [label ="Protection \nlevel", shape=diamond, fixedsize = true, width=1.2, height=0.8, margin=0.05];
      d18 [label ="FLC", shape=diamond, fixedsize = true, width=1.2, height=0.8, margin=0.05];
      d19 [label ="CB:150%\nF:150%"];
      d20 [label ="CB:167%\nF:167%"];
      d21 [label ="CB:300%\nF:300%"];
      d22 [label ="For side", shape=diamond, fixedsize = true, width=1.2, height=0.8, margin=0.05];
      d23 [label ="CB:125%\nF:125%"];
      d1 -> d15 [label="< 750V"];
      d15 -> d16 [label="Oil"];
      d15 -> d17 [label="Dry"];
      d16 -> d18 [label="Pri.\nonly"];
      d18 -> d19 [label="I >= 9A"];
      d18 -> d20 [label="9A > I >= 2A"];
      {rank=same; d19; d20;}
    d19 -> d20 [style=invis];
      d18 -> d21 [label="I < 2A"];
      d16 -> d22 [label="P & S"];
      d17 -> d22 [label="P & S"];
      d17 -> d23 [label="Pri.\nonly"];
      d22 -> d21 [label="Primary"];
      d22 -> d23 [label="Sec."];
    }
"""
