
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